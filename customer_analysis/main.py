import json
import datasets

# file = "./data/raw/All_Beauty.jsonl"     # e.g., "All_Beauty.jsonl", downloaded from the `review` link above
# with open(file, 'r') as fp:
#     print(type(fp))
#     for line in fp:
#         print(json.loads(line.strip()))
#         break

reviews = datasets.load_dataset(
    "McAuley-Lab/Amazon-Reviews-2023", f"raw_review_All_Beauty", trust_remote_code=True)["full"]
print(type(reviews))
for i in reviews:
    print(i)
    break