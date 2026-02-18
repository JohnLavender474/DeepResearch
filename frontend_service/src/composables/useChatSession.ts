import { ref, computed } from "vue";

import type ChatMessageViewModel from "@/model/chatMessageViewModel";
import type AIMessageContent from "@/model/aiMessageContent";
import type { ChatStatus } from "@/model/chatStatus";
import type Conversation from "@/model/conversation";
import type GraphStep from "@/model/graphStep";
import type UserQueryRequest from "@/model/userQueryRequest";
import {
  fetchConversation,
  fetchConversationsForProfile,
  createConversation,
} from "@/services/conversationService";
import { createChatTurn, updateChatTurn } from "@/services/chatTurnService";
import {
  streamGraphExecution,
  stopInvocation,
  type SimpleMessage,
} from "@/services/graphService";
import { fetchInvocation } from "@/services/invocationService";
import type { InvocationStatus } from "@/model/aiMessageContent";


const INVOCATION_POLL_INTERVAL = 3000;

export function useChatSession() {
  const messages = ref<Map<string, ChatMessageViewModel>>(new Map());
  const chatStatus = ref<ChatStatus>('idle');

  const conversations = ref<Conversation[]>([]);
  const isLoadingConversations = ref(false);  

  const currentConversationId = ref("");

  const currentProfileId = ref("");

  const activeInvocationId = ref("");

  const activeAiMessageId = ref("");

  const error = ref("");

  let invocationPollingIntervalId: number | null = null;

  let currentAbortController: AbortController | null = null;

  const stopPollingForInvocationData = () => {
    if (invocationPollingIntervalId !== null) {
      clearInterval(invocationPollingIntervalId);
      invocationPollingIntervalId = null;
      console.log("Stopped polling for invocation status");
    }
  };

  const pollForInvocationData = async (
    profileId: string,
    invocationId: string,
    messageId: string
  ) => {
    try {
      const invocation = await fetchInvocation(profileId, invocationId);

      const existingMessage = messages.value.get(messageId);

      if (existingMessage) {
        const oldContent = existingMessage.content as AIMessageContent;

        const updatedContent: AIMessageContent = {
          invocation_id: invocation.invocation_id,
          status: invocation.status as AIMessageContent['status'],
          steps: invocation.graph_state?.steps || [],
          final_result: invocation.graph_state?.current_result,
          error_message: invocation.graph_state?.error,
          latestBlurb: invocation.graph_state?.blurb,
        };

        if (JSON.stringify(oldContent.steps) !== JSON.stringify(updatedContent.steps)) {
          console.log(
            `Invocation ${invocationId} steps updated:`,
            updatedContent.steps
          );

          messages.value.set(messageId, {
            ...existingMessage,
            content: updatedContent,
          });
        }        

        if (
          invocation.status === 'completed' ||
          invocation.status === 'stopped' ||
          invocation.status === 'error'
        ) {
          chatStatus.value = 'idle';
          stopPollingForInvocationData();
          console.log(
            `Invocation ${invocationId} reached terminal state: ${invocation.status}`
          );
        }
      } else {
        console.warn(`Message with ID ${messageId} not found during polling`);
        stopPollingForInvocationData();
      }
    } catch (err) {
      console.error("Error polling invocation status:", err);
    }
  };

  const startPollingForInvocationData = (
    profileId: string,
    invocationId: string,
    messageId: string
  ) => {
    stopPollingForInvocationData();

    console.log(`Starting to poll invocation ${invocationId}`);

    invocationPollingIntervalId = window.setInterval(() => {
      pollForInvocationData(profileId, invocationId, messageId);
    }, INVOCATION_POLL_INTERVAL);

    pollForInvocationData(profileId, invocationId, messageId);
  };

  const stopCurrentInvocation = async () => {
    const invocationId = activeInvocationId.value;
    const profileId = currentProfileId.value;
    const messageId = activeAiMessageId.value;

    if (!invocationId || !profileId) {
      return;
    }

    if (currentAbortController) {
      currentAbortController.abort();
      currentAbortController = null;
    }

    stopPollingForInvocationData();

    if (messageId) {
      const existingMessage = messages.value.get(messageId);

      if (existingMessage) {
        const existing = existingMessage.content as AIMessageContent;

        messages.value.set(messageId, {
          ...existingMessage,
          content: {
            ...existing,
            status: 'stopped',
          } as AIMessageContent,
        });
      }
    }

    chatStatus.value = 'idle';

    try {
      await stopInvocation(
        invocationId,
        profileId,
      );

      console.log(
        `Stop request sent for invocation ${invocationId}`,
      );
    } catch (err) {
      console.error("Error stopping invocation:", err);
    }

    activeInvocationId.value = "";
    activeAiMessageId.value = "";
  };

  const loadConversations = async (profileId: string) => {
    if (!profileId) {
      conversations.value = [];
      return;
    }

    isLoadingConversations.value = true;

    try {
      conversations.value = await fetchConversationsForProfile(profileId);
    } catch (err) {
      console.error("Failed to fetch conversations:", err);
      conversations.value = [];
    } finally {
      isLoadingConversations.value = false;
    }
  };

  const loadConversation = async (
    conversationId: string,
    profileId: string,
  ) => {
    stopPollingForInvocationData();

    if (!conversationId) {
      console.warn("No conversation ID provided");

      messages.value = new Map();
      currentConversationId.value = "";

      return;
    }

    chatStatus.value = 'loading';

    error.value = "";
    
    try {
      const conversation = await fetchConversation(conversationId, profileId);

      if (conversation) {
        console.log("Loaded conversation:", conversation);
        
        currentConversationId.value = conversation.id;
        currentProfileId.value = profileId;
        
        const loadedMessages: ChatMessageViewModel[] = [];

        for (const turn of conversation.chat_turns) {
          if (turn.role === "human") {
            loadedMessages.push({
              id: turn.id,
              role: "user" as const,
              content: turn.data.content,
              timestamp: new Date(turn.timestamp),
            });
          } else {
            let aiContent: AIMessageContent = {
              status: 'running',
              steps: [],
            };

            if (turn.data.invocation_id) {
              try {
                const invocation = await fetchInvocation(
                  profileId,
                  turn.data.invocation_id,
                );

                aiContent = {
                  invocation_id: invocation.invocation_id,
                  status: invocation.status as AIMessageContent['status'],
                  steps: invocation.graph_state?.steps || [],
                  final_result: invocation.graph_state?.current_result,
                  error_message: invocation.graph_state?.error,
                };
              } catch (err) {
                console.error(
                  "Error loading invocation for chat turn:",
                  err,
                );

                aiContent = {
                  status: 'error',
                  steps: [],
                  error_message: 'Failed to load invocation data',
                };
              }
            }

            loadedMessages.push({
              id: turn.id,
              role: "ai" as const,
              content: aiContent,
              timestamp: new Date(turn.timestamp),
            });
          }
        }

        messages.value = new Map(
          loadedMessages.map((message) => [message.id, message]),
        );

        const lastMessage = loadedMessages[loadedMessages.length - 1];
        if (
          lastMessage &&
          lastMessage.role === 'ai' &&
          typeof lastMessage.content === 'object' &&
          lastMessage.content.status === 'running'
        ) {
          chatStatus.value = 'running';

          if (lastMessage.content.invocation_id) {
            activeInvocationId.value = lastMessage.content.invocation_id;
            activeAiMessageId.value = lastMessage.id;

            startPollingForInvocationData(
              profileId,
              lastMessage.content.invocation_id,
              lastMessage.id
            );
          }
        }
      } else {
        console.warn("Conversation not found");

        messages.value = new Map();
        currentConversationId.value = "";

        error.value = "Conversation not found";
      }
    } catch (err) {
      console.error("Error loading conversation:", err);

      error.value =
        err instanceof Error ? err.message : "Failed to load conversation";

      messages.value = new Map();
      currentConversationId.value = "";
    } finally {
      if (chatStatus.value === 'loading') {
        chatStatus.value = 'idle';
      }
    }
  };

  const createNewConversation = async (
    profileId: string,
    firstMessage: string,
  ): Promise<string> => {
    const title =
      firstMessage.substring(0, 50) + (firstMessage.length > 50 ? "..." : "");

    try {
      console.log("Creating conversation with title:", title);

      const conversation = await createConversation(profileId, title);

      currentConversationId.value = conversation.id;
      currentProfileId.value = profileId;

      console.log("Created conversation:", conversation);

      return conversation.id;
    } catch (err) {
      console.error("Error creating conversation:", err);

      error.value =
        err instanceof Error ? err.message : "Failed to create conversation";
      throw err;
    }
  };

  const submitMessage = async (
    request: UserQueryRequest,
    profileId: string,
  ) => {
    if (!request.query.trim()) {
      console.warn("Empty message submitted");
      error.value = "Please enter a message";
      return;
    }

    error.value = "";

    chatStatus.value = 'running';

    let activeConversationId = currentConversationId.value;

    if (!activeConversationId) {
      console.log("No active conversation, creating a new one");

      try {
        activeConversationId = await createNewConversation(profileId, request.query);

        loadConversations(profileId);
      } catch (err) {
        error.value =
          err instanceof Error ? err.message : "Failed to create conversation";

        chatStatus.value = 'idle';

        return;
      }
    }

    // The chat history is compiled here before adding the new user message and AI response
    // message to ensure the history sent to the backend reflects the state at the time of
    // the user query. 

    const chatHistory: SimpleMessage[] = Array.from(messages.value.values())
      .map((msg) => {
        if (msg.role === "user") {
          return {
            role: "human",
            content: msg.content as string,
          };
        } else {
          const aiContent = msg.content as AIMessageContent;
          return {
            role: "ai",
            content: aiContent.final_result || "",
          };
        }
      });

    const userTimestamp = new Date().toISOString();

    // Below, the new user message and the placeholder AI message are created 
    // before processing the graph execution stream to ensure they are properly
    // updated in both the frontend and the database.

    try {
      const userChatTurn = await createChatTurn(
        profileId,
        activeConversationId,
        "human",
        { content: request.query },
        userTimestamp,
      );

      console.log("Created user chat turn:", userChatTurn);

      messages.value.set(userChatTurn.id, {
        id: userChatTurn.id,
        role: "user",
        content: userChatTurn.data.content,
        timestamp: new Date(userChatTurn.timestamp),
      });
    } catch (err) {
      console.error("Error creating user chat turn:", err);
      error.value =
        err instanceof Error ? err.message : "Failed to save message";

      chatStatus.value = 'idle';

      return;
    }

    const aiTimestamp = new Date().toISOString();

    let aiChatTurnId: string | null = null;

    try {
      const aiChatTurn = await createChatTurn(
        profileId,
        activeConversationId,
        "ai",
        {},
        aiTimestamp,
      );

      aiChatTurnId = aiChatTurn.id;

      console.log("Created AI chat turn with ID:", aiChatTurnId);

      const initialAIContent: AIMessageContent = {
        status: 'running',
        steps: [],
      };

      messages.value.set(aiChatTurn.id, {
        id: aiChatTurn.id,
        role: "ai",
        content: initialAIContent,
        timestamp: new Date(aiChatTurn.timestamp),
      });
    } catch (err) {
      console.error("Error creating AI chat turn:", err);
      error.value =
        err instanceof Error ? err.message : "Failed to create AI turn";

      chatStatus.value = 'idle';

      return;
    }

    // Invoke the graph execution stream after both chat turns have been created to ensure 
    // the AI message can be updated with invocation data in real-time as it arrives. If the
    // stream is interrupted, then polling will pick up the invocation data and update the 
    // message accordingly when the user returns to the conversation.

    try {
      console.log("Starting graph execution stream for query:", request.query);    

      currentAbortController = new AbortController();

      const stream = streamGraphExecution(
        {
          user_query: request.query,
          profile_id: profileId,
          messages: chatHistory,
          execution_config: request.executionConfig
            ? {
                process_override: request.executionConfig.processOverride,
                model_selection: request.executionConfig.modelSelection,
                allow_general_knowledge_fallback:
                  request.executionConfig.allowGeneralKnowledgeFallback,                
                temperature: request.executionConfig.temperature,
                reasoning_level: request.executionConfig.reasoningLevel,
              }
            : undefined,
        },
        currentAbortController.signal,
      );

      let currentInvocationId: string | null = null;
      
      let currentSteps: GraphStep[] = [];
      let latestBlurb: string | undefined;

      let finalStatus: InvocationStatus = 'running';
      let finalResult: string | undefined;

      let errorMessage: string | undefined;

      for await (const chunk of stream) {
        try {
          const events = chunk.split("\n\n").filter(Boolean);

          for (const event of events) {
            if (event.startsWith("data: ")) {
              const jsonData = event.substring(6).trim();
              const parsedData = JSON.parse(jsonData);

              console.log("Stream event received:", parsedData);

              if (
                !currentInvocationId &&
                parsedData.invocation_id &&
                aiChatTurnId
              ) {
                console.log(
                  "Setting invocation ID on chat turn:",
                  parsedData.invocation_id,
                );

                currentInvocationId = parsedData.invocation_id;

                activeInvocationId.value = currentInvocationId ?? "";
                activeAiMessageId.value = aiChatTurnId;

                await updateChatTurn(profileId, aiChatTurnId, {
                  invocation_id: parsedData.invocation_id,
                });

                console.log("Invocation ID updated successfully");
              }

              if (parsedData.event_type === 'graph_complete') {
                finalStatus = 'completed';
              } else if (parsedData.event_type === 'stopped') {
                finalStatus = 'stopped';
              } else if (parsedData.event_type === 'error') {
                finalStatus = 'error';
                errorMessage = parsedData.event_value?.error;
              } else if (parsedData.event_type === 'blurb') {
                latestBlurb = parsedData.event_value?.content;
              }

              if (
                (parsedData.event_type === 'node_complete' ||
                  parsedData.event_type === 'heartbeat') &&
                currentInvocationId
              ) {
                try {
                  const invocation = await fetchInvocation(
                    profileId,
                    currentInvocationId,
                  );

                  currentSteps = invocation.graph_state?.steps || [];
                } catch (err) {
                  console.warn("Error fetching invocation for steps update:", err);
                }
              }

              const existingMessage = aiChatTurnId
                ? messages.value.get(aiChatTurnId)
                : undefined;

              if (existingMessage && aiChatTurnId) {
                const updatedContent: AIMessageContent = {
                  invocation_id: currentInvocationId || undefined,
                  status: finalStatus,
                  steps: [...currentSteps],
                  final_result: finalResult,
                  error_message: errorMessage,
                  latestBlurb: latestBlurb,
                };

                messages.value.set(aiChatTurnId, {
                  ...existingMessage,
                  content: updatedContent,
                });
              }
            }
          }
        } catch (parseError) {
          console.warn("Failed to parse stream chunk:", parseError);
        }
      }

      console.log("Graph execution stream completed");

      if (currentInvocationId) {
        try {
          const invocation = await fetchInvocation(
            profileId,
            currentInvocationId,
          );

          currentSteps = invocation.graph_state?.steps || [];
          finalResult = invocation.graph_state?.current_result;

          const existingMessage = aiChatTurnId
            ? messages.value.get(aiChatTurnId)
            : undefined;

          if (existingMessage && aiChatTurnId) {
            const updatedContent: AIMessageContent = {
              invocation_id: currentInvocationId,
              status: finalStatus,
              steps: [...currentSteps],
              final_result: finalResult,
              error_message: errorMessage,
            };

            messages.value.set(aiChatTurnId, {
              ...existingMessage,
              content: updatedContent,
            });
          }
        } catch (err) {
          console.error("Error fetching final invocation state:", err);
        }
      }

      if (currentInvocationId && aiChatTurnId) {
        console.log(
          "Updating chat turn with invocation ID:",
          currentInvocationId,
        );

        try {
          await updateChatTurn(profileId, aiChatTurnId, {
            invocation_id: currentInvocationId,
          });

          console.log("Chat turn updated successfully");
        } catch (err) {
          console.error("Error updating chat turn:", err);
        }
      }
    } catch (err) {
      if (err instanceof DOMException && err.name === 'AbortError') {
        console.log("Graph execution stream aborted by user");
      } else {
        console.error("Error during graph execution:", err);
        error.value = err instanceof Error ? err.message : "An error occurred";
      }
    } finally {
      if (chatStatus.value === 'running') {
        chatStatus.value = 'idle';
      }
      currentAbortController = null;
      activeInvocationId.value = "";
      activeAiMessageId.value = "";
    }
  };

  const clearChatSession = () => {
    stopPollingForInvocationData();

    if (currentAbortController) {
      currentAbortController.abort();
      currentAbortController = null;
    }

    messages.value = new Map();
    currentConversationId.value = "";
    currentProfileId.value = "";
    activeInvocationId.value = "";
    activeAiMessageId.value = "";    
    chatStatus.value = 'idle';
    error.value = "";
  };

  return {
    messages: computed(() => messages.value),
    conversations: computed(() => conversations.value),
    chatStatus: computed(() => chatStatus.value),
    isLoadingConversations: computed(() => isLoadingConversations.value),    
    currentConversationId: computed(() => currentConversationId.value),
    error: computed(() => error.value),
    loadConversations,
    loadConversation,
    createNewConversation,
    submitMessage,
    stopCurrentInvocation,
    clearChatSession,
  };
}
