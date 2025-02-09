import pandas as pd
import matplotlib.pyplot as plt
from transformers import pipeline as hf_pipeline
from datetime import datetime, timedelta
import random

class TransactionDataGenerator:
    def __init__(self):
        self.categories = {'Groceries': {'merchants': ['Walmart', 'Whole Foods'], 'amount_range': (10, 300)},'Dining': {'merchants': ['McDonald\'s', 'Starbucks'], 'amount_range': (5, 100)},'Transportation': {'merchants': ['Uber', 'Lyft'], 'amount_range': (5, 150)},'Shopping': {'merchants': ['Amazon', 'Target'], 'amount_range': (10, 500)},'Entertainment': {'merchants': ['Netflix', 'Spotify'], 'amount_range': (5, 80)},'Utilities': {'merchants': ['Electric Company', 'Water Utility'], 'amount_range': (30, 300)},'Healthcare': {'merchants': ['CVS Pharmacy', 'Walgreens'], 'amount_range': (10, 1000)}}
    def generate_date_range(self, start_date, num_days):
        return [start_date + timedelta(days=x) for x in range(num_days)]
    def generate_transaction(self, date):
        category = random.choice(list(self.categories.keys()))
        merchant_info = self.categories[category]
        merchant = random.choice(merchant_info['merchants'])
        amount = round(random.uniform(*merchant_info['amount_range']), 2)
        return {'Date': date, 'Description': merchant, 'Amount': amount, 'Category': category}
    def generate_dataset(self, num_transactions):
        start_date = datetime.now() - timedelta(days=30)
        date_range = self.generate_date_range(start_date, 30)
        transactions = [self.generate_transaction(random.choice(date_range)) for _ in range(num_transactions)]
        return pd.DataFrame(transactions).sort_values('Date').reset_index(drop=True)

class TransactionCategorizer:
    def __init__(self):
        self.classifier = hf_pipeline("zero-shot-classification", model="facebook/bart-large-mnli")
        self.candidate_labels = ['Groceries', 'Dining', 'Transportation', 'Shopping', 'Entertainment', 'Utilities', 'Healthcare']
    def categorize(self, data):
        descriptions = data['Description'].fillna('').tolist()
        results = [self.classifier(desc, self.candidate_labels)['labels'][0] for desc in descriptions]
        data['Predicted_Category'] = results
        return data

class SpendingRecommender:
    def __init__(self, state_tier):
        self.state_tier = state_tier
        self.categories = self._set_category_percentages()
    def _set_category_percentages(self):
        tier_adjustments = {'Tier 1': {'Groceries': 12, 'Dining': 10, 'Transportation': 18, 'Utilities': 8, 'Healthcare': 12, 'Entertainment': 6, 'Shopping': 8},'Tier 2': {'Groceries': 10, 'Dining': 8, 'Transportation': 14, 'Utilities': 7, 'Healthcare': 10, 'Entertainment': 7, 'Shopping': 6},'Tier 3': {'Groceries': 8, 'Dining': 6, 'Transportation': 10, 'Utilities': 6, 'Healthcare': 12, 'Entertainment': 5, 'Shopping': 5}}
        return tier_adjustments[self.state_tier]
    def get_recommendation_data(self, category_spending, total_spent):
        return {category: total_spent * (percent / 100) for category, percent in self.categories.items()}

class GoalPlanner:
    def __init__(self, total_savings):
        self.total_savings = total_savings
        self.goals = []
    def add_goal(self, name, amount, months):
        self.goals.append({'name': name, 'amount': amount, 'months': months, 'remaining_amount': amount})
    def plan_goals(self, monthly_savings):
        self.total_savings += monthly_savings
        for goal in sorted(self.goals, key=lambda x: x['months']):
            if goal['remaining_amount'] > 0 and goal['months'] > 0:
                monthly_contribution = goal['amount'] / goal['months']
                contribution = min(self.total_savings, monthly_contribution)
                goal['remaining_amount'] -= contribution
                self.total_savings -= contribution
                goal['months'] -= 1
        for goal in sorted(self.goals, key=lambda x: x['months']):
            if self.total_savings > 0 and goal['remaining_amount'] > 0:
                additional_contribution = min(self.total_savings, goal['remaining_amount'])
                goal['remaining_amount'] -= additional_contribution
                self.total_savings -= additional_contribution
        return {goal['name']: f"Remaining: ${goal['remaining_amount']:.2f}, Months Left: {goal['months']}" for goal in self.goals}
    def visualize_goals(self):
        labels = [goal['name'] for goal in self.goals]
        remaining_amounts = [goal['remaining_amount'] for goal in self.goals]
        funded_amounts = [goal['amount'] - goal['remaining_amount'] for goal in self.goals]
        plt.figure(figsize=(10, 6))
        plt.bar(labels, funded_amounts, color='green', label='Funded Amount')
        plt.bar(labels, remaining_amounts, bottom=funded_amounts, color='red', label='Remaining Amount')
        plt.xlabel('Goals')
        plt.ylabel('Amount ($)')
        plt.title('Goal Funding Progress')
        plt.xticks(rotation=45)
        plt.legend()
        plt.tight_layout()
        plt.show()

def main():
    state = input("Enter your state: ")
    tier_mapping = {'California': 'Tier 1', 'Texas': 'Tier 2', 'Iowa': 'Tier 3'}
    state_tier = tier_mapping.get(state, 'Tier 2')
    generator = TransactionDataGenerator()
    categorizer = TransactionCategorizer()
    recommender = SpendingRecommender(state_tier)
    total_savings = float(input("Enter your total savings: "))
    goal_planner = GoalPlanner(total_savings)
    num_goals = int(input("Enter number of goals: "))
    max_month = float("-inf")
    for _ in range(num_goals):
        name = input("Enter goal name: ")
        amount = float(input(f"Enter total amount for {name}: "))
        months = int(input(f"Enter months to achieve {name}: "))
        if months > max_month:
            max_month = months
        goal_planner.add_goal(name, amount, months)
    for month in range(1, max_month + 1):
        print(f"\nMonth {month}")
        print(f"Total Savings Before Expenses: ${goal_planner.total_savings:.2f}")
        csv_input = input("Do you want to upload a CSV file for this month? (yes/no): ")
        if csv_input.lower() == 'yes':
            csv_path = input("Enter the path to your CSV file: ")
            data = pd.read_csv(csv_path)
        else:
            data = generator.generate_dataset(200)
        categorized_data = categorizer.categorize(data)
        category_spending = categorized_data.groupby('Predicted_Category')['Amount'].sum().to_dict()
        total_spent = sum(category_spending.values())
        print(f"Actual Spending for Month {month}: ${total_spent:.2f}")
        recommended_spending = recommender.get_recommendation_data(category_spending, total_spent)
        print(f"Recommended Spending for Month {month}: ${sum(recommended_spending.values()):.2f}")
        if month == 1:
            monthly_savings = total_spent - sum(recommended_spending.values())
        else:
            monthly_savings = total_spent - sum(recommended_spending.values())
        plan = goal_planner.plan_goals(monthly_savings)
        for goal, status in plan.items():
            print(f"{goal}: {status}")
        print(f"Total Savings Left After Month {month}: ${goal_planner.total_savings:.2f}")
        goal_planner.visualize_goals()
        add_goal = input("Do you want to add a new goal? (yes/no): ")
        if add_goal.lower() == 'yes':
            name = input("Enter new goal name: ")
            amount = float(input(f"Enter total amount for {name}: "))
            months = int(input(f"Enter months to achieve {name}: "))
            goal_planner.add_goal(name, amount, months)
        if all(goal['remaining_amount'] <= 0 for goal in goal_planner.goals):
            print("All goals achieved!")
            break

if __name__ == "__main__":
    main()