from bot_app.services.location_service import location_client

def previous_location(msg):
    location_data = location_client.get_user_locations(msg.from_user.id)
    locations = location_data.get("locations", [])

    if not locations:
        return None, None

    text = ""
    buttons = []
    temp_row = []

    for count, loc_item in enumerate(locations[:15], start=1):
        loc = loc_item.get("location", {})
        name = loc.get("name", "Noma'lum manzil")
        text += f"{count}: {name}\n"

        temp_row.append(str(count))
        if len(temp_row) == 5:
            buttons.append(temp_row)
            temp_row = []

    if temp_row:
        buttons.append(temp_row)
    print(text, buttons)
    return text, buttons