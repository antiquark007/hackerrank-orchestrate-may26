"""
Main entry point: Process support tickets CSV and generate output
"""

import os
import sys
import pandas as pd
from pathlib import Path
from agent import SupportTriageAgent
import argparse
from dotenv import load_dotenv

def main():
    # Load environment variables
    load_dotenv()
    
    # Parse arguments
    parser = argparse.ArgumentParser(description="Support Triage Agent")
    parser.add_argument(
        "--input",
        default="../support_tickets/support_tickets.csv",
        help="Input CSV file with support tickets"
    )
    parser.add_argument(
        "--output",
        default="../support_tickets/output.csv",
        help="Output CSV file for triage results"
    )
    parser.add_argument(
        "--data",
        default="../data",
        help="Path to data directory with support corpus"
    )
    parser.add_argument(
        "--sample",
        action="store_true",
        help="Process sample tickets instead"
    )
    
    args = parser.parse_args()
    
    # Check API key
    if not os.getenv("GOOGLE_API_KEY"):
        print("ERROR: GOOGLE_API_KEY not set in .env")
        print("Get your FREE key from: https://ai.google.dev/")
        sys.exit(1)
    
    # Determine input file
    if args.sample:
        input_file = "../support_tickets/sample_support_tickets.csv"
    else:
        input_file = args.input
    
    input_path = Path(__file__).parent / input_file
    output_path = Path(__file__).parent / args.output
    data_dir = Path(__file__).parent / args.data
    
    print(f"Input: {input_path}")
    print(f"Output: {output_path}")
    print(f"Data: {data_dir}")
    
    if not input_path.exists():
        print(f"ERROR: Input file not found: {input_path}")
        sys.exit(1)
    
    # Initialize agent
    print("Initializing support triage agent...")
    agent = SupportTriageAgent(str(data_dir))
    
    # Load tickets
    print(f"Loading tickets from {input_path}...")
    df = pd.read_csv(input_path)
    print(f"Loaded {len(df)} tickets")
    
    # Process tickets
    results = []
    
    for idx, row in df.iterrows():
        print(f"Processing ticket {idx+1}/{len(df)}...", end="\r")
        
        issue = row.get("Issue", "")
        subject = row.get("Subject", "")
        company = row.get("Company", "")
        
        # Handle NaN values
        if pd.isna(issue):
            issue = ""
        if pd.isna(subject):
            subject = ""
        if pd.isna(company):
            company = ""
        
        try:
            triage_result = agent.process_ticket(issue, subject, company)
            results.append(triage_result)
        except Exception as e:
            print(f"Error processing ticket {idx}: {e}")
            # Fallback response
            results.append({
                "status": "escalated",
                "product_area": "error_processing",
                "response": "Could not process this ticket due to an internal error.",
                "justification": f"Error: {str(e)}",
                "request_type": "invalid"
            })
    
    print(f"\nCompleted processing {len(results)} tickets")
    
    # Create output dataframe
    output_df = pd.DataFrame(results)
    
    # Ensure correct column order
    columns = ["Status", "Product Area", "Response", "Justification", "Request Type"]
    output_df.columns = ["status", "product_area", "response", "justification", "request_type"]
    output_df.columns = columns
    
    # Save output
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_df.to_csv(output_path, index=False)
    print(f"Results saved to {output_path}")
    
    # Print summary
    print("\n=== SUMMARY ===")
    print(f"Total tickets: {len(results)}")
    print(f"Replied: {sum(1 for r in results if r['status'] == 'replied')}")
    print(f"Escalated: {sum(1 for r in results if r['status'] == 'escalated')}")

if __name__ == "__main__":
    main()
