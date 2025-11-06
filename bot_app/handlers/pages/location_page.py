from telebot.states.sync import StateContext
from telebot.types import Message
from bot_app.services.location_service import location_client
from bot_app.repo.user_service import BotUserService
from msg_app.models import BotMessage
from ..pages.order_page import order
from ..pages.start_now_page import start_now
from ...core.loader import bot
from ...functions.buttons.default import create_btn
from ...functions.buttons.inline import travel_control_inl
from ...functions.distance import calc_distance
from ...functions.get_place import get_place_from_coords
from ...functions.text_sender import send_msg
from ...functions.utils import del_msg
from ...core.states import TravelState
from .previous_locations_page import previous_location
import logging

# Configure logger
logger = logging.getLogger(__name__)

# =========================================================
# 🔹 Constants
# =========================================================
PRICE_PER_KM = 500
MAX_PREVIOUS_LOCATIONS = 10  # Prevent index overflow


class LocationService:
    """Service class for location-related operations"""

    @staticmethod
    def create_location_dict(lat: float, lng: float, address: str = None,
                             heading: float = None, live_period: int = None,
                             accuracy: float = None) -> dict:
        """Create standardized location dictionary"""
        return {
            "address": address or "",
            "lat": lat,
            "lng": lng,
            "heading": heading,
            "live_period": live_period,
            "accuracy": accuracy
        }


# =========================================================
# 🔹 Universal location detection
# =========================================================
def detect_location(msg: Message, state: StateContext, state_key: str) -> dict | None:
    """
    Detect location from message and save to database

    Returns:
        dict: Location data if successful, None if location required
    """
    if not getattr(msg, "location", None):
        _request_location(msg, state, state_key)
        return None

    try:
        location = _process_gps_location(msg)
        _save_location_to_db(msg.from_user.id, location)
        state.add_data(**{state_key: location})
        return location

    except Exception as e:
        logger.error(f"Location detection failed for user {msg.from_user.id}: {e}")
        _request_location(msg, state, state_key)
        return None


def _process_gps_location(msg: Message) -> dict:
    """Process GPS location from message"""
    coords_data = get_place_from_coords(
        msg.location.latitude,
        msg.location.longitude
    )

    return LocationService.create_location_dict(
        lat=msg.location.latitude,
        lng=msg.location.longitude,
        address=coords_data.get("full_address", "Unknown address"),
        heading=getattr(msg.location, 'heading', None),
        live_period=getattr(msg.location, 'live_period', None),
        accuracy=getattr(msg.location, 'horizontal_accuracy', None)
    )


def _save_location_to_db(telegram_id: int, location: dict):
    """Save location to database"""
    location_client.create_user_location(
        telegram_id=telegram_id,
        address=location["address"],
        lat=location["lat"],
        lng=location["lng"],
        heading=location["heading"],
        live_period=location["live_period"],
        accuracy=location["accuracy"]
    )


def _request_location(msg: Message, state: StateContext, state_key: str):
    """Request location from user"""
    del_msg(bot, msg)
    state.set(getattr(TravelState, state_key))
    send_msg(
        "send_exact_location",
        msg,
        [["send_location"], ["back_order"]],
        create_btn
    )


# =========================================================
# 🔹 Previous location selection
# =========================================================
def select_previous_location(msg: Message, state: StateContext, loc_key: str) -> bool:
    """
    Select location from previous locations by index

    Returns:
        bool: True if selection successful
    """
    if not msg.text or not msg.text.isdigit():
        return False

    index = int(msg.text) - 1
    location_data = location_client.get_user_locations(msg.from_user.id)
    locations = location_data.get("locations", [])

    # Validate index range
    if not (0 <= index < len(locations) and index < MAX_PREVIOUS_LOCATIONS):
        return False

    loc_item = locations[index]["location"]
    location = LocationService.create_location_dict(
        lat=loc_item.get("lat"),
        lng=loc_item.get("lng"),
        address=loc_item.get("name")
    )

    state.add_data(**{loc_key: location})
    return True


# =========================================================
# 🔹 Start location handler
# =========================================================
def loc_begin(msg: Message, state: StateContext):
    """Handle start location selection"""
    user_id = msg.from_user.id
    lang = BotUserService.get_lang(user_id)

    # Handle back button
    if _is_back_button(msg, lang):
        return _handle_back_to_order(msg, state)

    # Handle previous location selection
    if select_previous_location(msg, state, "loc_begin"):
        return _handle_previous_location_selected(msg, state)

    # Handle new location
    location = detect_location(msg, state, "loc_begin")
    if location:
        _handle_new_start_location(msg, state, location)


def _is_back_button(msg: Message, lang: str) -> bool:
    """Check if message is back button"""
    return BotMessage.get_slug(lang, getattr(msg, "text", "")) == "back"


def _handle_back_to_order(msg: Message, state: StateContext):
    """Handle navigation back to order page"""
    state.delete()
    del_msg(bot, msg, 2)
    return order(msg, state)


def _handle_previous_location_selected(msg: Message, state: StateContext):
    """Handle when user selects previous location"""
    state.set(TravelState.loc_end)

    with state.data() as data:
        location = data.get("loc_begin", {})

    text, button_rows = previous_location(msg)
    if text and button_rows:
        return send_msg(
            "confirm_start_location",
            msg,
            [["send_location"]] + button_rows + [["back_order"]],
            markup=create_btn,
            loc_begin=location.get("address", ""),
            info=text
        )


def _handle_new_start_location(msg: Message, state: StateContext, location: dict):
    """Handle new GPS location for start"""
    state.set(TravelState.loc_end)
    return send_msg(
        "ask_destination",
        msg,
        [["send_location"], ["back_order"]],
        markup=create_btn,
        loc_begin=location.get("address", "")
    )


# =========================================================
# 🔹 Destination location handler
# =========================================================
def loc_end(msg: Message, state: StateContext):
    """Handle destination location selection"""
    user_id = msg.from_user.id
    lang = BotUserService.get_lang(user_id)

    # Handle back button
    if _is_back_button(msg, lang):
        return _handle_back_to_start(msg, state)

    # Handle location selection
    location = _get_destination_location(msg, state)
    if not location:
        return

    # Calculate price and show trip details
    _show_trip_details(msg, state, location, lang)


def _handle_back_to_start(msg: Message, state: StateContext):
    """Handle navigation back to start page"""
    state.delete()
    return start_now(msg, state)


def _get_destination_location(msg: Message, state: StateContext) -> dict | None:
    """Get destination location from message"""
    # Try previous location first
    if select_previous_location(msg, state, "loc_end"):
        with state.data() as data:
            return data.get("loc_end")

    # Try new location
    return detect_location(msg, state, "loc_end")


def _show_trip_details(msg: Message, state: StateContext, location: dict, lang: str):
    """Calculate and display trip details"""
    with state.data() as data:
        loc_begin = data.get("loc_begin", {})

        # Calculate distance and price
        dist_km = calc_distance(
            loc_begin.get("lat", 0),
            loc_begin.get("lng", 0),
            location.get("lat", 0),
            location.get("lng", 0)
        )
        price = int(dist_km * PRICE_PER_KM)
        state.add_data(**{"price": price, "loc_end": location})

    state.set(TravelState.details)

    return send_msg(
        "trip_details",
        msg,
        [1, "economy", False],
        markup=travel_control_inl,
        loc_begin=loc_begin.get("address", "Unknown"),
        loc_end=location.get("address", "Unknown"),
        passenger=1,
        travel_class=BotMessage.get_txt(lang, "economy"),
        price=price,
        has_woman="❌"
    )