// claude.ts - Claude Integration for The Outworld Scraper
import axios from "axios";
import * as dotenv from "dotenv";

// Load environment variables
dotenv.config();

const CLAUDE_API_KEY = process.env.CLAUDE_API_KEY;
const API_BASE_URL = "https://api.anthropic.com/v1/messages";

interface ClaudeMessage {
  role: "user" | "assistant";
  content: string;
}

interface ClaudeResponse {
  content: Array<{
    type: string;
    text: string;
  }>;
  model: string;
  usage: {
    input_tokens: number;
    output_tokens: number;
  };
}

class ClaudeScrapingAssistant {
  private async callClaude(messages: ClaudeMessage[], model: string = "claude-3-haiku-20240307"): Promise<string> {
    try {
      const response = await axios.post<ClaudeResponse>(
        API_BASE_URL,
        {
          model: model, // Using Haiku for faster responses
          max_tokens: 1024,
          messages: messages,
        },
        {
          headers: {
            "x-api-key": CLAUDE_API_KEY,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
          },
        }
      );

      return response.data.content[0]?.text || "No response from Claude";
    } catch (error) {
      console.error("❌ Error calling Claude API:", error);
      throw error;
    }
  }

  // 🔍 Analyze scraping results
  async analyzeScrapingResults(eventData: string): Promise<void> {
    console.log("🔍 Analyzing scraping results with Claude...");
    
    const messages: ClaudeMessage[] = [
      {
        role: "user",
        content: `As a data analysis expert, analyze these scraped events from Denver:

${eventData}

Please provide:
1. Quality assessment of the events
2. Missing information that should be scraped
3. Suggestions for improving event descriptions
4. Categorization recommendations

Be concise and actionable.`
      }
    ];

    const analysis = await this.callClaude(messages);
    console.log("📊 CLAUDE ANALYSIS:");
    console.log(analysis);
  }

  // 🛠️ Generate scraper improvements
  async suggestScraperImprovements(scraperCode: string, scraperName: string): Promise<void> {
    console.log(`🛠️ Getting Claude suggestions for ${scraperName} scraper...`);
    
    const messages: ClaudeMessage[] = [
      {
        role: "user",
        content: `Review this Python scraper code for "${scraperName}" and suggest improvements:

\`\`\`python
${scraperCode}
\`\`\`

Focus on:
1. Error handling improvements
2. Performance optimizations
3. Anti-ban measures
4. Data quality improvements
5. Code structure and maintainability

Provide specific, actionable suggestions.`
      }
    ];

    const suggestions = await this.callClaude(messages);
    console.log(`🔧 CLAUDE SUGGESTIONS FOR ${scraperName.toUpperCase()}:`);
    console.log(suggestions);
  }

  // 📝 Generate event descriptions
  async enhanceEventDescriptions(events: any[]): Promise<void> {
    console.log("📝 Enhancing event descriptions with Claude...");
    
    const eventSummary = events.slice(0, 5).map(event => 
      `Title: ${event.title}\nCurrent Description: ${event.description}\nLocation: ${event.location_name}\n---`
    ).join('\n');

    const messages: ClaudeMessage[] = [
      {
        role: "user",
        content: `Improve these event descriptions for a family events website in Denver. Make them more engaging and informative while keeping them concise (max 150 words each):

${eventSummary}

For each event, provide:
1. Enhanced description that's family-friendly
2. Key highlights for parents
3. Age-appropriate messaging`
      }
    ];

    const enhancedDescriptions = await this.callClaude(messages);
    console.log("✨ ENHANCED DESCRIPTIONS:");
    console.log(enhancedDescriptions);
  }

  // 🎯 Generate test queries
  async generateTestQueries(): Promise<void> {
    console.log("🎯 Generating test queries with Claude...");
    
    const messages: ClaudeMessage[] = [
      {
        role: "user",
        content: `Generate 10 realistic test queries that families in Denver might search for when looking for events. Consider:

- Different age groups (toddlers, kids, teens)
- Various activities (indoor, outdoor, educational, entertainment)
- Seasonal considerations
- Price considerations (free vs paid)
- Weekend vs weekday preferences

Format as a simple list.`
      }
    ];

    const queries = await this.callClaude(messages);
    console.log("🔍 SUGGESTED TEST QUERIES:");
    console.log(queries);
  }

  // 💡 Get coding help
  async getCodingHelp(question: string): Promise<void> {
    console.log("💡 Getting coding help from Claude...");
    
    const messages: ClaudeMessage[] = [
      {
        role: "user",
        content: `I'm working on "The Outworld Scraper" - a Python web scraping project for family events in Denver. 

Current tech stack:
- Python with FastAPI
- BeautifulSoup for scraping
- Supabase for database
- 6 active scrapers: Library, Kids Out About, Movies, Hiking, Children's Museum, Denver Zoo

Question: ${question}

Please provide specific, practical advice with code examples if relevant.`
      }
    ];

    const help = await this.callClaude(messages);
    console.log("🤖 CLAUDE'S CODING ADVICE:");
    console.log(help);
  }
}

// 🚀 Command line interface
async function main() {
  const assistant = new ClaudeScrapingAssistant();
  
  const command = process.argv[2];
  const input = process.argv[3];

  console.log("🤖 CLAUDE SCRAPING ASSISTANT");
  console.log("=" .repeat(40));

  try {
    switch (command) {
      case "analyze":
        if (!input) {
          console.log("Usage: npm run claude-ts analyze 'event data string'");
          return;
        }
        await assistant.analyzeScrapingResults(input);
        break;

      case "improve":
        if (!input) {
          console.log("Usage: npm run claude-ts improve 'scraper_name'");
          return;
        }
        // This would normally read the scraper file
        await assistant.suggestScraperImprovements("# Placeholder scraper code", input);
        break;

      case "enhance":
        console.log("📝 This would enhance event descriptions from the database");
        await assistant.enhanceEventDescriptions([]);
        break;

      case "queries":
        await assistant.generateTestQueries();
        break;

      case "help":
        if (!input) {
          console.log("Usage: npm run claude-ts help 'your coding question'");
          return;
        }
        await assistant.getCodingHelp(input);
        break;

      default:
        console.log(`
🎯 Available commands:

analyze "event data"     - Analyze scraped events
improve scraper_name     - Get scraper improvement suggestions  
enhance                  - Enhance event descriptions
queries                  - Generate test search queries
help "question"          - Get coding help

Examples:
npm run claude-ts queries
npm run claude-ts help "How to avoid IP bans in web scraping?"
npm run claude-ts analyze "Event: Summer Camp at Library..."
        `);
    }
  } catch (error) {
    console.error("❌ Error:", error);
  }
}

// Run if called directly
if (import.meta.url === `file://${process.argv[1]}`) {
  main();
} 