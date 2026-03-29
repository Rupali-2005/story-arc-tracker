import os
import requests
from dotenv import load_dotenv

load_dotenv()

def check_claims(claims: list) -> list:
    """
    Takes the factual_claims list from analyzer.py
    and attempts to verify checkable ones via
    Google's Fact Check API. Falls back gracefully
    if nothing is found.
    """
    results = []

    for item in claims:
        claim_text = item.get("claim", "")
        checkable = item.get("checkable", False)
        existing_verdict = item.get("verdict", "Unverifiable")

        if not checkable:
            results.append({
                "claim": claim_text,
                "checkable": False,
                "verdict": "Not checkable",
                "source": None
            })
            continue

        # Hit Google Fact Check API
        try:
            url = "https://factchecktools.googleapis.com/v1alpha1/claims:search"
            params = {
                "query": claim_text,
                "languageCode": "en"
            }
            response = requests.get(url, params=params)
            data = response.json()

            claims_found = data.get("claims", [])

            if claims_found:
                top = claims_found[0]
                review = top.get("claimReview", [{}])[0]
                results.append({
                    "claim": claim_text,
                    "checkable": True,
                    "verdict": review.get("textualRating", existing_verdict),
                    "source": review.get("url", None),
                    "reviewer": review.get("publisher", {}).get("name", "Unknown")
                })
            else:
                # No external result found, keep AI verdict
                results.append({
                    "claim": claim_text,
                    "checkable": True,
                    "verdict": existing_verdict,
                    "source": None,
                    "reviewer": "AI Assessment"
                })

        except Exception as e:
            results.append({
                "claim": claim_text,
                "checkable": True,
                "verdict": existing_verdict,
                "source": None,
                "reviewer": "AI Assessment"
            })

    return results


# Quick test
if __name__ == "__main__":
    sample_claims = [
        {
            "claim": "India has 14 crore demat accounts",
            "checkable": True,
            "verdict": "Likely True"
        },
        {
            "claim": "The government has completely failed",
            "checkable": False,
            "verdict": "Unverifiable"
        }
    ]

    results = check_claims(sample_claims)
    for r in results:
        print(r)