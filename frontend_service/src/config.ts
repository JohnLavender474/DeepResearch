import { DEBUG_ALLOW_DUMMY_AI_KEY } from "@/constants";


export function isDummyAiAllowed(): boolean {
  const allowDummyAI = localStorage.getItem(DEBUG_ALLOW_DUMMY_AI_KEY);
  return allowDummyAI === 'true';
}