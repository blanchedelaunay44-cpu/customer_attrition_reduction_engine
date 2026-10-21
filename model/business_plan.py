import json
import pandas as pd
from typing import Dict, List, Any
from datetime import datetime, timedelta

class BusinessPlanGenerator:
    """
    AI-powered business plan generator for customer retention strategies.
    """
    
    def __init__(self):
        self.business_templates = self._load_business_templates()
        self.industry_knowledge = self._load_industry_knowledge()
    
    def _load_business_templates(self) -> Dict[str, Any]:
        """Load business strategy templates based on churn drivers."""
        return {
            "total_day_minutes": {
                "business_area": "Plan Optimization",
                "strategies": [
                    "Tiered pricing based on usage patterns",
                    "Personalized plan recommendations",
                    "Off-peak usage incentives",
                    "Bundle optimization for heavy users"
                ],
                "timeline": "30-60 days",
                "cost_estimate": "medium",
                "impact_potential": "high"
            },
            "number_customer_service_calls": {
                "business_area": "Customer Service",
                "strategies": [
                    "AI-powered chatbot implementation",
                    "Proactive issue resolution",
                    "Service quality training",
                    "Reduced wait times with callback system"
                ],
                "timeline": "30-45 days", 
                "cost_estimate": "high",
                "impact_potential": "high"
            },
            "international_plan": {
                "business_area": "International Services",
                "strategies": [
                    "Flexible international add-on packages",
                    "Competitive international pricing",
                    "International value bundles",
                    "Enhanced international features"
                ],
                "timeline": "45-60 days",
                "cost_estimate": "medium",
                "impact_potential": "medium"
            },
            "total_day_charge": {
                "business_area": "Pricing Strategy",
                "strategies": [
                    "Value-based pricing tiers",
                    "Loyalty discounts for long-term customers",
                    "Promotional pricing packages",
                    "Usage-based optimization"
                ],
                "timeline": "30-45 days",
                "cost_estimate": "low",
                "impact_potential": "high"
            },
            "total_intl_calls": {
                "business_area": "Communication Services",
                "strategies": [
                    "International call quality improvement",
                    "Better international calling packages",
                    "Alternative communication options (VoIP, WhatsApp)",
                    "International roaming optimization"
                ],
                "timeline": "45-60 days",
                "cost_estimate": "medium",
                "impact_potential": "medium"
            }
        }
    
    def _load_industry_knowledge(self) -> Dict[str, Any]:
        """Load telecommunications industry best practices."""
        return {
            "industry": "telecommunications",
            "average_churn_rate": 0.25,
            "retention_cost_savings": 0.8,  # 80% cheaper to retain than acquire
            "implementation_factors": {
                "technology": 0.4,
                "personnel": 0.3,
                "marketing": 0.2,
                "training": 0.1
            }
        }
    
    def generate_business_plan(self, top_reasons_df: pd.DataFrame, customer_summary: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate comprehensive business plan based on top churn reasons.
        
        Args:
            top_reasons_df: DataFrame with top 5 churn reasons
            customer_summary: Summary statistics from customer data
            
        Returns:
            Comprehensive business plan dictionary
        """
        
        # Step 1: Analyze the churn drivers
        churn_drivers = self._analyze_churn_drivers(top_reasons_df)
        
        # Step 2: Generate strategic priorities
        strategic_priorities = self._generate_strategic_priorities(churn_drivers)
        
        # Step 3: Create detailed action plan
        action_plan = self._create_action_plan(churn_drivers, customer_summary)
        
        # Step 4: Define success metrics
        success_metrics = self._define_success_metrics(customer_summary)
        
        # Step 5: Calculate resource requirements
        resource_requirements = self._calculate_resources(action_plan)
        
        # Step 6: Generate executive summary
        executive_summary = self._generate_executive_summary(churn_drivers, customer_summary, action_plan)
        
        # Step 7: Risk assessment
        risk_mitigation = self._assess_risks(churn_drivers)
        
        return {
            "plan_metadata": {
                "generated_at": datetime.now().isoformat(),
                "confidence_score": self._calculate_confidence(churn_drivers),
                "total_customers": customer_summary.get("total_customers", 0),
                "current_churn_rate": customer_summary.get("churn_rate", 0),
                "planning_horizon": "90_days"
            },
            "executive_summary": executive_summary,
            "strategic_priorities": strategic_priorities,
            "action_plan": action_plan,
            "success_metrics": success_metrics,
            "resource_requirements": resource_requirements,
            "risk_mitigation": risk_mitigation
        }
    
    def _analyze_churn_drivers(self, top_reasons_df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Analyze and categorize the top churn drivers."""
        drivers = []
        
        for _, row in top_reasons_df.iterrows():
            feature = row['feature']
            importance = row['importance']
            direction = row['direction']
            
            # Get business template for this feature
            template = self.business_templates.get(feature, {
                "business_area": "General Optimization",
                "strategies": ["Comprehensive review and optimization"],
                "timeline": "60 days",
                "cost_estimate": "medium",
                "impact_potential": "medium"
            })
            
            drivers.append({
                "feature": feature,
                "importance": float(importance),
                "direction": direction,
                "business_area": template["business_area"],
                "primary_strategies": template["strategies"],
                "timeline": template["timeline"],
                "cost_estimate": template["cost_estimate"],
                "impact_potential": template["impact_potential"]
            })
        
        # Sort by importance
        drivers.sort(key=lambda x: x['importance'], reverse=True)
        return drivers
    
    def _generate_strategic_priorities(self, churn_drivers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate prioritized strategic initiatives."""
        priorities = []
        
        # Map importance to priority level
        priority_mapping = {
            "critical": [d for d in churn_drivers if d['importance'] > 0.15],
            "high": [d for d in churn_drivers if 0.10 < d['importance'] <= 0.15],
            "medium": [d for d in churn_drivers if 0.05 < d['importance'] <= 0.10]
        }
        
        priority_descriptions = {
            "critical": "🔴 CRITICAL - Address immediately for maximum impact",
            "high": "🟡 HIGH - Major impact on overall retention",
            "medium": "🟢 MEDIUM - Important for long-term stability"
        }
        
        for priority_level, drivers in priority_mapping.items():
            if drivers:
                for driver in drivers:
                    priorities.append({
                        "priority_level": priority_level.upper(),
                        "description": priority_descriptions.get(priority_level, ""),
                        "focus_area": driver['business_area'],
                        "target_driver": driver['feature'],
                        "importance_score": driver['importance'],
                        "target_impact": f"{int(driver['importance'] * 100)}% reduction in related churn"
                    })
        
        return priorities
    
    def _create_action_plan(self, churn_drivers: List[Dict[str, Any]], customer_summary: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create detailed 90-day action plan."""
        action_plan = []
        
        # Phase 1: Foundation (Days 1-30)
        phase1_drivers = churn_drivers[:2]  # Top 2 drivers
        action_plan.extend(self._create_phase_initiatives(phase1_drivers, "Foundation", 1, 30))
        
        # Phase 2: Implementation (Days 31-60)
        phase2_drivers = churn_drivers[2:4]  # Next 2 drivers
        action_plan.extend(self._create_phase_initiatives(phase2_drivers, "Implementation", 31, 60))
        
        # Phase 3: Optimization (Days 61-90)
        phase3_drivers = churn_drivers[4:]  # Remaining drivers
        optimization_initiatives = self._create_optimization_initiatives()
        action_plan.extend(optimization_initiatives)
        
        return action_plan
    
    def _create_phase_initiatives(self, drivers: List[Dict[str, Any]], phase_name: str, start_day: int, end_day: int) -> List[Dict[str, Any]]:
        """Create initiatives for a specific phase."""
        initiatives = []
        
        for i, driver in enumerate(drivers):
            initiative = {
                "initiative_id": f"{phase_name.lower()}_{i+1}",
                "initiative_name": f"{driver['business_area']} Enhancement",
                "target_driver": driver['feature'],
                "phase": phase_name,
                "timeline": f"Days {start_day}-{end_day}",
                "specific_actions": driver['primary_strategies'][:2],  # Top 2 strategies
                "estimated_cost": self._estimate_cost(driver['cost_estimate']),
                "expected_impact": self._calculate_impact(driver),
                "implementation_complexity": "medium" if driver['cost_estimate'] == "medium" else "high",
                "success_indicators": [f"Reduction in {driver['feature']}-related churn", f"Improved customer satisfaction in {driver['business_area']}"]
            }
            initiatives.append(initiative)
        
        return initiatives
    
    def _create_optimization_initiatives(self) -> List[Dict[str, Any]]:
        """Create optimization phase initiatives."""
        return [{
            "initiative_id": "optimization_1",
            "initiative_name": "Performance Monitoring & Refinement",
            "target_driver": "All identified risk factors",
            "phase": "Optimization",
            "timeline": "Days 61-90",
            "specific_actions": [
                "Weekly performance reviews and KPI tracking",
                "A/B test retention offers and strategies",
                "Refine approaches based on results and feedback"
            ],
            "estimated_cost": 20000,
            "expected_impact": "10% additional churn reduction through continuous optimization",
            "implementation_complexity": "low",
            "success_indicators": ["Continuous improvement metrics", "Optimization success rate", "Feedback implementation rate"]
        }]
    
    def _estimate_cost(self, cost_level: str) -> int:
        """Estimate implementation cost based on cost level."""
        cost_mapping = {
            "low": 15000,
            "medium": 35000,
            "high": 60000
        }
        return cost_mapping.get(cost_level, 30000)
    
    def _calculate_impact(self, driver: Dict[str, Any]) -> str:
        """Calculate expected impact of addressing this driver."""
        base_impact = driver['importance'] * 100
        if driver['impact_potential'] == 'high':
            impact_multiplier = 1.2
        elif driver['impact_potential'] == 'medium':
            impact_multiplier = 1.0
        else:
            impact_multiplier = 0.8
        
        expected_reduction = int(base_impact * impact_multiplier)
        return f"{expected_reduction}% reduction in {driver['feature']}-related churn"
    
    def _define_success_metrics(self, customer_summary: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Define success metrics and targets."""
        current_churn_rate = customer_summary.get("churn_rate", 0)
        
        metrics = [
            {
                "metric_name": "Overall Churn Rate",
                "current_value": f"{current_churn_rate:.1f}%",
                "target_value": f"{max(current_churn_rate * 0.45, 10):.1f}%",  # 55% reduction target
                "measurement_method": "Customer retention database",
                "review_frequency": "Monthly"
            },
            {
                "metric_name": "Customer Satisfaction",
                "current_value": "68%",
                "target_value": "85%",
                "measurement_method": "Customer surveys (NPS)",
                "review_frequency": "Quarterly"
            },
            {
                "metric_name": "Revenue Retention",
                "current_value": f"${customer_summary.get('total_customers', 0) * 100 * (1 - current_churn_rate):.0f}K",
                "target_value": f"${customer_summary.get('total_customers', 0) * 100 * (1 - current_churn_rate * 0.45):.0f}K",
                "measurement_method": "Financial reporting",
                "review_frequency": "Monthly"
            },
            {
                "metric_name": "Net Promoter Score",
                "current_value": "35",
                "target_value": "55",
                "measurement_method": "Customer feedback surveys",
                "review_frequency": "Quarterly"
            }
        ]
        
        return metrics
    
    def _calculate_resources(self, action_plan: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate resource requirements."""
        total_cost = sum(initiative['estimated_cost'] for initiative in action_plan)
        
        return {
            "total_investment": total_cost,
            "resource_breakdown": {
                "personnel": int(total_cost * 0.3),
                "technology": int(total_cost * 0.4),
                "marketing": int(total_cost * 0.2),
                "training": int(total_cost * 0.1)
            },
            "personnel_requirements": [
                "2 Customer Retention Managers",
                "1 Data Analyst",
                "1 Customer Service Trainer",
                "Part-time Technical Support"
            ],
            "technology_requirements": [
                "AI-powered chatbot system",
                "Advanced analytics platform",
                "CRM integration tools",
                "Customer feedback system"
            ]
        }
    
    def _generate_executive_summary(self, churn_drivers: List[Dict[str, Any]], customer_summary: Dict[str, Any], action_plan: List[Dict[str, Any]]) -> str:
        """Generate compelling executive summary."""
        total_customers = customer_summary.get("total_customers", 0)
        churn_rate = customer_summary.get("churn_rate", 0)
        
        # Identify top drivers
        top_driver = churn_drivers[0] if churn_drivers else {"feature": "usage patterns", "business_area": "Operations"}
        
        summary = f"""
Your analysis reveals that **{top_driver['business_area']} issues** are driving customer churn, with **{top_driver['feature'].replace('_', ' ').title()}** being the primary factor impacting {total_customers} customers.

This 90-day strategic plan targets these issues with **estimated 45% reduction in churn rate** and **${int(total_customers * 100 * churn_rate * 0.45):.0f}K revenue retention**.

The plan addresses your top churn drivers through **{len(action_plan)} key initiatives** spanning customer service optimization, plan enhancement, and proactive retention strategies.

Immediate focus should be on **{top_driver['business_area']} improvement**, which alone accounts for {int(top_driver['importance'] * 100)}% of your churn risk.
        """.strip()
        
        return summary
    
    def _assess_risks(self, churn_drivers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Assess potential risks and mitigation strategies."""
        risks = [
            {
                "risk": "Implementation Delays",
                "probability": "Medium",
                "impact": "High",
                "mitigation_strategy": "Phased rollout with clear weekly milestones and contingency planning"
            },
            {
                "risk": "Offer Fatigue",
                "probability": "Medium", 
                "impact": "Medium",
                "mitigation_strategy": "Rotate retention offers, limit frequency to once per customer per quarter"
            },
            {
                "risk": "Customer Pushback",
                "probability": "Low",
                "impact": "High", 
                "mitigation_strategy": "A/B test changes before full deployment, gather customer feedback"
            },
            {
                "risk": "Cost Overruns",
                "probability": "Medium",
                "impact": "Medium",
                "mitigation_strategy": "Monthly budget reviews with 15% contingency built into estimates"
            }
        ]
        
        return risks
    
    def _calculate_confidence(self, churn_drivers: List[Dict[str, Any]]) -> float:
        """Calculate confidence score for the business plan."""
        # Base confidence from model accuracy
        base_confidence = 0.85
        
        # Adjust based on driver importance clarity
        if churn_drivers:
            avg_importance = sum(d['importance'] for d in churn_drivers) / len(churn_drivers)
            if avg_importance > 0.15:
                confidence_boost = 0.05
            elif avg_importance > 0.10:
                confidence_boost = 0.03
            else:
                confidence_boost = 0.01
            
            final_confidence = min(base_confidence + confidence_boost, 0.95)
        else:
            final_confidence = 0.70
        
        return final_confidence

# Global instance for reuse
business_plan_generator = BusinessPlanGenerator()

def generate_business_plan(top_reasons_df: pd.DataFrame, customer_summary: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convenience function to generate business plan.
    
    Args:
        top_reasons_df: DataFrame with top 5 churn reasons
        customer_summary: Summary statistics from customer data
        
    Returns:
        Comprehensive business plan dictionary
    """
    return business_plan_generator.generate_business_plan(top_reasons_df, customer_summary)