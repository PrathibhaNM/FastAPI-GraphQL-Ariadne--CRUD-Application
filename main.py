from fastapi import FastAPI
from ariadne import QueryType, MutationType, graphql_sync, make_executable_schema, ObjectType
from ariadne.asgi import GraphQL

from pymongo import MongoClient
from bson import ObjectId

# Initialize FastAPI
app = FastAPI()

# Initialize MongoDB client
dbURL="mongodb+srv://prathibhanm081306:Prathibha13@cluster0.zobjf3r.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(dbURL)
db = client["test_db"]
collection = db["items"]

# Define GraphQL types
type_defs = """
    type Query {
        items: [Item]
        item(id: ID!): Item
    }
    type Item {
        id: ID!
        name: String!
        description: String!
    }
    type Mutation {
        createItem(name: String!, description: String!): Item
        updateItem(id: ID!, name: String!, description: String!): Item
        deleteItem(id: ID!): String
    }
"""

# Define resolvers
query = QueryType()
mutation = MutationType()


# @query.field("items")
# def resolve_items(_, info):
#     return list(collection.find())



@query.field("items")
def resolve_items(_, info):
    items = list(collection.find())
    for item in items:
        item["id"] = str(item["_id"])  # Convert ObjectId to string for id field
        del item["_id"]  # Remove the original _id field
    return items

# @query.field("item")
# def resolve_item(_, info, id):
#     item = collection.find_one({"_id": ObjectId(id)})
#     if item:
#         # Ensure that the id field is returned as a string
#         item["_id"] = str(item["_id"])
#         return item
#     else:
#         return None


@query.field("item")
def resolve_item(_, info, id):
    item = collection.find_one({"_id": ObjectId(id)})
    if item:
        # Ensure that the id field is returned as a string
        item["id"] = str(item["_id"])
        del item["_id"]
        return item
    else:
        return None



@mutation.field("createItem")
def resolve_create_item(_, info, name, description):
    item_id = collection.insert_one({"name": name, "description": description}).inserted_id
    return {"id": str(item_id), "name": name, "description": description}


@mutation.field("updateItem")
def resolve_update_item(_, info, id, name, description):
    collection.update_one({"_id": ObjectId(id)}, {"$set": {"name": name, "description": description}})
    return {"id": id, "name": name, "description": description}




# @mutation.field("deleteItem")
# def resolve_delete_item(_, info, id):
#     item = collection.find_one({"_id": ObjectId(id)})
#     if item:
#         collection.delete_one({"_id": ObjectId(id)})
#         item["_id"] = str(item["_id"])  # Convert ObjectId to string for id field
#         del item["_id"]  # Remove the original _id field
#         return item
#     else:
#         raise ValueError("Item not found")

@mutation.field("deleteItem")
def resolve_delete_item(_, info, id):
    item = collection.find_one({"_id": ObjectId(id)})
    if item:
        collection.delete_one({"_id": ObjectId(id)})
        return "Item deleted successfully"
    else:
        raise ValueError("Item not found")


# Create executable GraphQL schema
schema = make_executable_schema(type_defs, [query, mutation])

# Define GraphQL endpoint
app.add_route("/graphql", GraphQL(schema, debug=True))
