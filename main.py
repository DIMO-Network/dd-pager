import requests
import sys

vehicle_query = """
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

definition_query = """
query PageDefinitions($after: String) {
    vehicles(first: 100, after: $after) {
        pageInfo {
            hasNextPage
            endCursor
        }
        nodes {
            definition {
                id
            }
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
                "query": vehicle_query,
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


def find_used_definitions() -> list[str]:
    definition_ids = set()
    after = None

    while True:
        resp = requests.post(
            "https://identity-api.dimo.zone/query",
            json={
                "query": definition_query,
                "variables": {"after": after},
            },
        )

        inner = resp.json()["data"]["vehicles"]

        for v in inner["nodes"]:
            if v["definition"]["id"] is not None:
                definition_ids.add(v["definition"]["id"])

        page_info = inner["pageInfo"]

        if not page_info["hasNextPage"]:
            break

        after = page_info["endCursor"]

    return list(definition_ids)


if __name__ == "__main__":
    if len(sys.argv) == 1:
        print('Provide a sub-command, either "dd-vehicles" or "dds"')
        sys.exit(1)

    sub_command = sys.argv[1]
    if sub_command == "dd-vehicles":
        if len(sys.argv) < 3:
            print("Provide device definition id")
            sys.exit(1)
        definition_id = sys.argv[2]
        for i in find_vehicles_with_definition(definition_id):
            print(i)
    elif sub_command == "dds":
        for s in find_used_definitions():
            print(s)
    else:
        print("Unrecognized sub-command {}".format(sub_command))
        sys.exit(1)