
type AgentProvider = 'openai' | 'langchain'; // update if you have other providers

type AssistantToolType = 'code_interpreter' | 'file_search' | 'function';

interface AssistantTool {
    type: AssistantToolType;
}

interface ToolResources {
    file_search?: Record<string, string[]> | null;
    code_interpreter?: Record<string, string[]> | null;
}

type ResponseFormatType = 'json_object' | 'json_schema';

interface AssistantResponseFormatOption {
    type: ResponseFormatType;
    json_schema?: Record<string, any> | null;
}

interface OpenAIProviderConfig {
    tools?: AssistantTool[] | null;
    tool_resources?: ToolResources | null;
    response_format?: AssistantResponseFormatOption | null;
    metadata?: Record<string, string> | null;
    temperature?: number | null;
    top_p?: number | null;
}

interface LangChainProviderConfig {
    chain_name?: string | null;
    memory_backend?: string | null;
    retriever_config?: Record<string, any> | null;
}

export interface IAgent {
    id: string
    name: string
    provider: string
    model: string
    user_instructions: string
    instructions: string
    assistant_id: string
    openai_config?: OpenAIProviderConfig | null;
    langchain_config?: LangChainProviderConfig | null;
    default?: boolean | null;
    created_at: string
}

export interface IAgentCreate {
    name: string;
    provider: string;
    model: string;
    user_instructions: string | null
    instructions: null;
    storage: string[];
    assistant_id?: string | null;
    openai_config?: any;
    langchain_config?: any;
    default?: boolean;
}