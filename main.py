import requests
import sys

query = """
query PageDefinitionVehicles($deviceDefinitionId: String!, $after: String) {
    vehicles(first: 100, filterBy: {deviceDefinitionId: $deviceDefinitionId}, after: $after) {
        pageInfo {
            hasNextPage
            endCursor
        }
        nodes {
            tokenId
        }
    }
}
"""


def find_vehicles_with_definition(definition_id: str) -> list[int]:
    token_ids = []
    after = None

    while True:
        resp = requests.post(
            "https://identity-api.dimo.zone/query",
            json={
                "query": query,
                "variables": {"deviceDefinitionId": definition_id, "after": after},
            },
        )

        inner = resp.json()["data"]["vehicles"]

        for v in inner["nodes"]:
            token_ids.append(v["tokenId"])

        page_info = inner["pageInfo"]

        if not page_info["hasNextPage"]:
            break

        after = page_info["endCursor"]

    return token_ids


if __name__ == "__main__":
    if len(sys.argv) == 1:
        print("Provide a device definition id")
        sys.exit(1)

    definition_id = sys.argv[1]
    for i in find_vehicles_with_definition(definition_id):
        print(i)
