// API Response Types

// Decision State - Aligns with backend Phase 7
export type DecisionState = 'RECOMMENDED' | 'ACCEPTED' | 'CUSTOMIZED' | 'OVERRIDDEN';

// Decision Context - Tracks user modifications
export interface DecisionContext {
  state: DecisionState;
  originalResults: AnalysisResponse | null;
  customizations?: CustomizationParams;
  overrideArchitecture?: string;
  decisionTimestamp?: string;
  decisionReason?: string;
}

// Customization parameters for Phase 7
export interface CustomizationParams {
  cpu?: number;
  ram?: number;
  region?: string;
  instances?: number;
  minInstances?: number;
  maxInstances?: number;
  storageType?: string;
  storageSizeGb?: number;
}

// Phase 7 Decision Request
export interface Phase7DecisionRequest {
  session_id: string;
  decision_type: 'accepted' | 'customized' | 'rejected';
  customization_details?: CustomizationParams;
  selected_alternative?: string;
  user_feedback?: string;
  decision_time_seconds?: number;
}

// Phase 1: Intent Capture
export interface IntentAnalysis {
  workload_type: string;
  requirements: {
    latency: string;
    availability: string;
    geography: string;
    compliance: string[];
  };
  constraints: {
    budget_sensitivity: string;
    team_experience: string;
    time_to_market: string;
  };
  scale: {
    monthly_users: number;
    estimated_rps: number;
    data_volume_gb: number;
  };
  parsing_confidence: number;
  key_requirements: string[];
}

export interface BusinessContext {
  workload_category: string;
  scale_tier: string;
  complexity_score: number;
  estimated_cloud_spend: {
    low: number;
    medium: number;
    high: number;
    currency: string;
  };
  risk_level: string;
}

export interface Phase1Result {
  status: string;
  intent_analysis: IntentAnalysis;
  business_context: BusinessContext;
  input_metadata: {
    raw_input: string;
    word_count: number;
  };
  processing_metadata: {
    gemini_mode: string;
    processing_time_ms: number;
  };
}

// Phase 2: Architecture Selection
export interface ArchitectureAlternative {
  architecture: string;
  when_to_consider: string;
}

export interface ArchitectureAnalysis {
  primary_architecture: string;
  confidence: number;
  reasoning: string;
  alternatives: ArchitectureAlternative[];
  selection_method: string;
}

export interface Phase2Result {
  status: string;
  architecture_analysis: ArchitectureAnalysis;
  processing_metadata: {
    processing_time_ms: number;
  };
}

// Phase 3: Machine Specification
export interface SpecificationAnalysis {
  machine_family: string;
  machine_size: string;
  exact_type: string;
  cpu: number;
  ram: number;
  confidence: number;
  sizing_rationale: string;
  catalog_match: string;
}

export interface ConfigurationDetails {
  region: string;
  instances: number;
  auto_scaling: {
    enabled: boolean;
    min_instances: number;
    max_instances: number;
  };
  storage: {
    type: string;
    size_gb: number;
  };
  networking: {
    vpc: boolean;
    load_balancer: boolean;
  };
}

export interface Phase3Result {
  status: string;
  specification_analysis: SpecificationAnalysis;
  configuration: ConfigurationDetails;
  processing_metadata: {
    processing_time_ms: number;
  };
}

// Phase 4: Pricing
export interface PriceBreakdown {
  compute: number;
  storage: number;
  networking: number;
  other: number;
}

export interface PrimaryPrice {
  total_monthly_usd: number;
  breakdown: PriceBreakdown;
  currency: string;
  billing_period: string;
}

export interface AlternativePrice {
  architecture: string;
  total_monthly_usd: number;
  difference_percent: number;
}

export interface SavingsAnalysis {
  potential_savings_percent: number;
  cheapest_alternative: string;
  savings_recommendations: string[];
}

export interface Phase4Result {
  status: string;
  primary_price: PrimaryPrice;
  alternative_prices: Record<string, number> | AlternativePrice[];
  accuracy_estimate: number;
  savings_analysis: SavingsAnalysis;
  processing_metadata: {
    calculation_method: string;
    processing_time_ms: number;
  };
}

// Phase 5: Trade-off Analysis
export interface TradeoffScore {
  factor: string;
  score: number;
  weight: number;
  preference: string;
}

export interface ProCon {
  point: string;
  impact: string;
}

export interface RiskItem {
  risk: string;
  severity: string;
  mitigation: string;
}

export interface TradeoffAnalysis {
  recommendation_strength: string;
  overall_score: number;
  pros: ProCon[];
  cons: ProCon[];
  risks: RiskItem[];
  analysis_method: string;
}

export interface Phase5Result {
  status: string;
  tradeoff_analysis: TradeoffAnalysis;
  tradeoff_scores: TradeoffScore[];
  decision_factors: {
    primary_factors: string[];
    secondary_factors: string[];
  };
  processing_metadata: {
    processing_time_ms: number;
  };
}

// Phase 6: Recommendation Presentation
export interface FinalRecommendation {
  headline: string;
  summary: string;
  confidence_score: number;
  key_benefits: string[];
  implementation_time: string;
}

export interface VisualComponents {
  cost_summary: {
    monthly_cost: number;
    annual_cost: number;
    cost_tier: string;
  };
  architecture_diagram: {
    primary_service: string;
    supporting_services: string[];
  };
  comparison_table: {
    columns: string[];
    rows: Array<{ [key: string]: string | number }>;
  };
}

export interface Phase6Result {
  status: string;
  presentation: {
    type: string;
    recommendation: FinalRecommendation;
    executive_summary: string;
  };
  visual_components: VisualComponents;
  consolidated_data: {
    workload_type: string;
    architecture: string;
    machine_type: string;
    monthly_cost: number;
    region: string;
  };
  processing_metadata: {
    processing_time_ms: number;
  };
}

// Generic phase result for backward compatibility
export interface PhaseResult {
  status: string;
  [key: string]: any;
}

export interface AnalysisResponse {
  status: 'processing' | 'completed' | 'error';
  session_id: string;
  phases: {
    phase1?: Phase1Result;
    phase2?: Phase2Result;
    phase3?: Phase3Result;
    phase4?: Phase4Result;
    phase5?: Phase5Result;
    phase6?: Phase6Result;
  };
}

export interface ErrorResponse {
  error: boolean;
  message: string;
  code: string;
}
