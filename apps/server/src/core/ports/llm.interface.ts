export interface LLM {
  process(prompt: string): Promise<string>;
  maxTokens: number;
}
