import { ref, computed } from "vue";

import type ChatMessageViewModel from "@/model/chatMessageViewModel";
import type AIMessageContent from "@/model/aiMessageContent";
import type Conversation from "@/model/conversation";
import type GraphStep from "@/model/graphStep";
import type UserQueryRequest from "@/model/userQueryRequest";
import {
  fetchConversation,
  fetchConversationsForProfile,
  createConversation,
} from "@/services/conversationService";
import { createChatTurn, updateChatTurn } from "@/services/chatTurnService";
import { streamGraphExecution, type SimpleMessage } from "@/services/graphService";
import { fetchInvocation } from "@/services/invocationService";


const INVOCATION_POLL_INTERVAL = 3000;

export function useChatSession() {
  const messages = ref<ChatMessageViewModel[]>([]);
  const conversations = ref<Conversation[]>([]);

  const isProcessing = ref(false);
  const isLoadingConversation = ref(false);
  const isLoadingConversations = ref(false);

  const error = ref("");

  const currentConversationId = ref("");
  const currentProfileId = ref("");

  let pollingIntervalId: number | null = null;

  const stopPolling = () => {
    if (pollingIntervalId !== null) {
      clearInterval(pollingIntervalId);
      pollingIntervalId = null;
      console.log("Stopped polling for invocation status");
    }
  };

  const pollInvocationStatus = async (
    profileId: string,
    invocationId: string,
    messageId: string
  ) => {
    try {
      const invocation = await fetchInvocation(profileId, invocationId);

      const messageIndex = messages.value.findIndex((m) => m.id === messageId);      

      if (messageIndex !== -1) {
        const oldContent = messages.value[messageIndex].content as AIMessageContent;

        const updatedContent: AIMessageContent = {
          invocation_id: invocation.invocation_id,
          status: invocation.status as AIMessageContent['status'],
          steps: invocation.graph_state?.steps || [],
          final_result: invocation.graph_state?.current_result,
          error_message: invocation.graph_state?.error,
        };

        if (JSON.stringify(oldContent.steps) !== JSON.stringify(updatedContent.steps)) {
          console.log(
            `Invocation ${invocationId} steps updated:`,
            updatedContent.steps
          );

          messages.value[messageIndex].content = updatedContent;
        }        

        if (
          invocation.status === 'completed' ||
          invocation.status === 'stopped' ||
          invocation.status === 'error'
        ) {
          isProcessing.value = false;
          stopPolling();
          console.log(
            `Invocation ${invocationId} reached terminal state: ${invocation.status}`
          );
        }
      } else {
        console.warn(`Message with ID ${messageId} not found during polling`);
        stopPolling();
      }
    } catch (err) {
      console.error("Error polling invocation status:", err);
    }
  };

  const startPolling = (
    profileId: string,
    invocationId: string,
    messageId: string
  ) => {
    stopPolling();

    console.log(`Starting to poll invocation ${invocationId}`);

    pollingIntervalId = window.setInterval(() => {
      pollInvocationStatus(profileId, invocationId, messageId);
    }, INVOCATION_POLL_INTERVAL);

    pollInvocationStatus(profileId, invocationId, messageId);
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
    stopPolling();

    if (!conversationId) {
      console.warn("No conversation ID provided");

      messages.value = [];
      currentConversationId.value = "";

      return;
    }

    isLoadingConversation.value = true;
    isProcessing.value = false;

    error.value = "";
    
    try {
      const conversation = await fetchConversation(conversationId, profileId);

      if (conversation) {
        console.log("Loaded conversation:", conversation);
        
        currentConversationId.value = conversation.id;
        currentProfileId.value = profileId;
        
        const loadedMessages = [];

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

        messages.value = loadedMessages;

        const lastMessage = loadedMessages[loadedMessages.length - 1];
        if (
          lastMessage &&
          lastMessage.role === 'ai' &&
          typeof lastMessage.content === 'object' &&
          lastMessage.content.status === 'running'
        ) {
          isProcessing.value = true;

          if (lastMessage.content.invocation_id) {
            startPolling(
              profileId,
              lastMessage.content.invocation_id,
              lastMessage.id
            );
          }
        }
      } else {
        console.warn("Conversation not found");
        
        messages.value = [];
        currentConversationId.value = "";

        error.value = "Conversation not found";
      }
    } catch (err) {
      console.error("Error loading conversation:", err);

      error.value =
        err instanceof Error ? err.message : "Failed to load conversation";

      messages.value = [];
      currentConversationId.value = "";
    } finally {
      isLoadingConversation.value = false;
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

    isProcessing.value = true;

    let activeConversationId = currentConversationId.value;

    if (!activeConversationId) {
      console.log("No active conversation, creating a new one");

      try {
        activeConversationId = await createNewConversation(profileId, request.query);

        loadConversations(profileId);
      } catch (err) {
        error.value =
          err instanceof Error ? err.message : "Failed to create conversation";

        isProcessing.value = false;

        return;
      }
    }

    const chatHistory: SimpleMessage[] = messages.value      
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

    try {
      const userChatTurn = await createChatTurn(
        profileId,
        activeConversationId,
        "human",
        { content: request.query },
        userTimestamp,
      );

      console.log("Created user chat turn:", userChatTurn);

      messages.value.push({
        id: userChatTurn.id,
        role: "user",
        content: userChatTurn.data.content,
        timestamp: new Date(userChatTurn.timestamp),
      });
    } catch (err) {
      console.error("Error creating user chat turn:", err);
      error.value =
        err instanceof Error ? err.message : "Failed to save message";

      isProcessing.value = false;

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

      messages.value.push({
        id: aiChatTurn.id,
        role: "ai",
        content: initialAIContent,
        timestamp: new Date(aiChatTurn.timestamp),
      });
    } catch (err) {
      console.error("Error creating AI chat turn:", err);
      error.value =
        err instanceof Error ? err.message : "Failed to create AI turn";

      isProcessing.value = false;

      return;
    }

    try {
      console.log("Starting graph execution stream for query:", request.query);    

      const stream = streamGraphExecution({
        user_query: request.query,
        profile_id: profileId,
        messages: chatHistory,
        process_override: request.processOverride,
        model_selection: request.modelSelection,
      });

      let invocationIdSet = false;
      let currentInvocationId: string | null = null;
      
      let currentSteps: GraphStep[] = [];

      let finalStatus: AIMessageContent['status'] = 'running';
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
                !invocationIdSet &&
                parsedData.invocation_id &&
                aiChatTurnId
              ) {
                console.log(
                  "Setting invocation ID on chat turn:",
                  parsedData.invocation_id,
                );

                currentInvocationId = parsedData.invocation_id;

                await updateChatTurn(profileId, aiChatTurnId, {
                  invocation_id: parsedData.invocation_id,
                });
                invocationIdSet = true;

                console.log("Invocation ID updated successfully");
              }

              if (parsedData.event_type === 'graph_complete') {
                finalStatus = 'completed';
              } else if (parsedData.event_type === 'stopped') {
                finalStatus = 'stopped';
              } else if (parsedData.event_type === 'error') {
                finalStatus = 'error';
                errorMessage = parsedData.event_value?.error;
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

              const messageIndex = messages.value.findIndex(
                (m) => m.id === aiChatTurnId,
              );

              if (messageIndex !== -1) {
                const updatedContent: AIMessageContent = {
                  invocation_id: currentInvocationId || undefined,
                  status: finalStatus,
                  steps: [...currentSteps],
                  final_result: finalResult,
                  error_message: errorMessage,
                };

                messages.value[messageIndex].content = updatedContent;
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

          const messageIndex = messages.value.findIndex(
            (m) => m.id === aiChatTurnId,
          );

          if (messageIndex !== -1) {
            const updatedContent: AIMessageContent = {
              invocation_id: currentInvocationId,
              status: finalStatus,
              steps: [...currentSteps],
              final_result: finalResult,
              error_message: errorMessage,
            };

            messages.value[messageIndex].content = updatedContent;
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
      console.error("Error during graph execution:", err);
      error.value = err instanceof Error ? err.message : "An error occurred";
    } finally {
      isProcessing.value = false;
    }
  };

  const clearChatSession = () => {
    stopPolling();
    messages.value = [];
    currentConversationId.value = "";
    currentProfileId.value = "";
    error.value = "";
    isProcessing.value = false;
  };

  return {
    messages: computed(() => messages.value),
    conversations: computed(() => conversations.value),
    isProcessing: computed(() => isProcessing.value),
    isLoadingConversation: computed(() => isLoadingConversation.value),
    isLoadingConversations: computed(() => isLoadingConversations.value),
    error: computed(() => error.value),
    currentConversationId: computed(() => currentConversationId.value),
    loadConversations,
    loadConversation,
    createNewConversation,
    submitMessage,
    clearChatSession,
    setError: (errorMessage: string) => {
      error.value = errorMessage;
    },
  };
}
