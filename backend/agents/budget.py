from .base_agent import BaseAgent
import json

class BudgetAgent(BaseAgent):
    """
    Specialized agent for travel budget planning and cost estimation
    """
    def __init__(self):
        system_prompt = """You are a travel budget planning expert AI agent. Your role is to:
1. Estimate travel costs based on destination, duration, and travel style
2. Break down expenses by category (flights, accommodation, food, activities, transport)
3. Provide budget-saving tips and alternatives
4. Consider seasonality and regional price variations

Format your response as JSON with:
- total_estimate: overall budget estimate
- breakdown: object with categories and costs
- currency: currency used
- savings_tips: array of money-saving suggestions
- budget_level: budget/moderate/luxury

Be realistic and helpful with practical advice."""
        
        super().__init__("BudgetAgent", system_prompt)

    def handle_request(self, input_data):
        """
        Process user query and return budget recommendations
        """
        try:
            user_prompt = f"""User Query: {input_data}
            
Please provide a detailed budget estimate for this trip.
Include breakdown by expense category and money-saving tips."""

            llm_response = self._call_llm(user_prompt)
            
            try:
                budget_data = json.loads(llm_response)
                return {"budget_info": budget_data}
            except json.JSONDecodeError:
                pass
            
            return {
                "budget_info": llm_response
            }
            
        except Exception as e:
            print(f"BudgetAgent error: {str(e)}")
            return {
                "budget_info": f"Unable to generate budget estimate. Error: {str(e)}"
            }
