/* eslint-disable no-console */

import type { LLM } from '../../core/ports';

import axios from 'axios';

export class OpenRouterAdapter implements LLM {
  private apiKey: string;
  private model: string;
  maxTokens = 10_000; // ~8192 tokens equivalent

  constructor(apiKey: string, model = 'openai/gpt-4o') {
    this.apiKey = apiKey;
    this.model = model;
  }

  async process(prompt: string): Promise<string> {
    try {
      const response = await axios.post(
        'https://openrouter.ai/api/v1/chat/completions',
        {
          model: this.model,
          messages: [
            {
              role: 'user',
              content: prompt,
            },
          ],
        },
        {
          headers: {
            Authorization: `Bearer ${this.apiKey}`,
            'Content-Type': 'application/json',
          },
          timeout: 120_000, // 2 minutes timeout
        },
      );

      const content = response.data.choices[0]?.message?.content;
      if (!content) {
        throw new Error('No content in OpenRouter response');
      }

      return content;
    } catch (error) {
      console.error('❌ Error in OpenRouter LLM:', error);
      throw new Error(`Failed to process with OpenRouter: ${error}`);
    }
  }
}
