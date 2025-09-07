# Author: Dhaval Patel. Codebasics YouTube Channel

from fastapi import FastAPI
from fastapi import Request
from fastapi.responses import JSONResponse
import db_helper
import generic_helper

app = FastAPI()

inprogress_orders = {}

@app.post("/")
async def handle_request(request: Request):
    # Retrieve the JSON data from the request
    payload = await request.json()

    # Extract the necessary information from the payload
    # based on the structure of the WebhookRequest from Dialogflow
    intent = payload['queryResult']['intent']['displayName']
    parameters = payload['queryResult']['parameters']
    output_contexts = payload['queryResult']['outputContexts']
    session_id = generic_helper.extract_session_id(output_contexts[0]["name"])

    intent_handler_dict = {
        'order.add-contest-ongoing order': add_to_order,
        'order.remove-context:ongoing-order': remove_from_order,
        'order.complete context:ongoing-order': complete_order,
        'track.order-context:ongoing-tracking': track_order
    }

    if intent not in intent_handler_dict:
        return JSONResponse(content={
            "fulfillmentText": f"Sorry, I cannot handle the intent: {intent}"
        })

    return intent_handler_dict[intent](parameters, session_id)


def save_to_db(order: dict):
    next_order_id = db_helper.get_next_order_id()

    for food_item, quantity in order.items():
        rcode = db_helper.insert_order_item(food_item, quantity, next_order_id)
        if rcode == -1:
            return -1

    db_helper.insert_order_tracking(next_order_id, "in progress")
    return next_order_id


def complete_order(parameters: dict, session_id: str):
    if session_id not in inprogress_orders:
        fulfillment_text = "I'm having trouble finding your order. Can you place a new one, please?"
    else:
        order = inprogress_orders[session_id]
        order_id = save_to_db(order)
        if order_id == -1:
            fulfillment_text = "Sorry, I couldn't process your order due to a backend error. Please try again."
        else:
            order_total = db_helper.get_total_order_price(order_id)
            fulfillment_text = (
                f"Awesome! We have placed your order. "
                f"Here is your order id # {order_id}. "
                f"Your order total is {order_total}, payable at delivery."
            )
        del inprogress_orders[session_id]

    return JSONResponse(content={"fulfillmentText": fulfillment_text})


def add_to_order(parameters: dict, session_id: str):
    food_items = parameters.get("food-item", [])
    quantities = parameters.get("number", [])

    if len(food_items) != len(quantities):
        fulfillment_text = "Sorry, I didn't understand. Please specify food items and quantities clearly."
    else:
        new_food_dict = dict(zip(food_items, quantities))

        if session_id in inprogress_orders:
            current_food_dict = inprogress_orders[session_id]
            for item, qty in new_food_dict.items():
                current_food_dict[item] = current_food_dict.get(item, 0) + qty
            inprogress_orders[session_id] = current_food_dict
        else:
            inprogress_orders[session_id] = new_food_dict

        order_str = generic_helper.get_str_from_food_dict(inprogress_orders[session_id])
        fulfillment_text = f"So far you have: {order_str}. Do you need anything else?"

    return JSONResponse(content={"fulfillmentText": fulfillment_text})


def remove_from_order(parameters: dict, session_id: str):
    if session_id not in inprogress_orders:
        return JSONResponse(content={
            "fulfillmentText": "I'm having trouble finding your order. Can you place a new one, please?"
        })

    food_items = parameters.get("food-item", [])
    current_order = inprogress_orders[session_id]

    removed_items, no_such_items = [], []

    for item in food_items:
        if item in current_order:
            removed_items.append(item)
            del current_order[item]
        else:
            no_such_items.append(item)

    messages = []
    if removed_items:
        messages.append(f"Removed {', '.join(removed_items)} from your order.")
    if no_such_items:
        messages.append(f"Your current order does not have {', '.join(no_such_items)}.")

    if not current_order:
        messages.append("Your order is now empty!")
    else:
        order_str = generic_helper.get_str_from_food_dict(current_order)
        messages.append(f"Here is what is left in your order: {order_str}")

    fulfillment_text = " ".join(messages)

    return JSONResponse(content={"fulfillmentText": fulfillment_text})


def track_order(parameters: dict, session_id: str):
    # Support both "order_id" and "number" from Dialogflow
    order_id = parameters.get("order_id") or parameters.get("number")

    if not order_id:
        return JSONResponse(content={
            "fulfillmentText": "Please provide a valid order ID."
        })

    order_status = db_helper.get_order_status(int(order_id))
    if order_status:
        fulfillment_text = f"The order status for order id #{order_id} is: {order_status}"
    else:
        fulfillment_text = f"No order found with order id #{order_id}"

    return JSONResponse(content={"fulfillmentText": fulfillment_text})