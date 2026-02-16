import discord
from discord.ui import Select

from src.commons.CommonFunctions import retry_on_ssl_error, check_if_user_can_interact_with_view, convert_to_png, \
    interaction_guard


#************************************************************************************
#-------------------------------------------BUTTONS---------------------------------------------
#************************************************************************************
# Placeholder button that does nothing when clicked
def create_dummy_label_button(label_text, row=1):
    button = discord.ui.Button(label=f"{label_text}", style=discord.ButtonStyle.gray, row=row)
    button.callback = dummy_callback()
    return button
def dummy_callback():
    async def callback(interaction):
        # Just acknowledge the interaction to prevent the "interaction failed" message
        # Without doing anything else
        await interaction.response.defer(ephemeral=True, thinking=False)
    return callback

# Creates an invisible button that serves as a spacer
def create_spacer_button(row=0):
    button = discord.ui.Button(label="\u200b",   style=discord.ButtonStyle.gray, disabled=True, row=row)
    button.callback = dummy_callback()
    return button

# todo
def create_navigation_button(is_next, view_instance, callback_func = None, row=0, disabled=False):
    button = discord.ui.Button(label="To Next Page➡️" if is_next else "⬅️To Previous Page", style=discord.ButtonStyle.blurple,  row=row,  disabled=disabled)
    button.callback = callback_func if callback_func else create_generic_nav_callback(view_instance, is_next)
    return button
def create_generic_nav_callback(view_instance, is_next):
    @retry_on_ssl_error(max_retries=3, delay=1)
    async def callback(interaction):
        if not await check_if_user_can_interact_with_view(interaction, view_instance.interaction_lock, view_instance.message_author.user_id):
            return

        async with view_instance.interaction_lock:
            await interaction.response.defer()

            # Determine new page based on view type
            if hasattr(view_instance, 'encyclopedia_image_factory'):
                current_page = view_instance.encyclopedia_image_factory.page_num
                new_page = current_page + 1 if is_next else current_page - 1
                new_image = view_instance.encyclopedia_image_factory.reload_image(new_page_number=new_page)
            elif hasattr(view_instance, 'encyclopedia_location_index_image_factory'):
                current_page = view_instance.encyclopedia_location_index_image_factory.page_num
                new_page = current_page + 1 if is_next else current_page - 1
                new_image = view_instance.encyclopedia_location_index_image_factory.reload_image(new_page_number=new_page)
            elif hasattr(view_instance, 'creature_inventory_image_factory'):
                current_box = view_instance.creature_inventory_image_factory.current_box_num
                new_box = current_box + 1 if is_next else current_box - 1

                if is_next and new_box > view_instance.max_boxes:
                    await interaction.followup.send_modal(view_instance.create_inventory_expansion_confirmation_modal())
                    return

                new_image = view_instance.creature_inventory_image_factory.get_creature_inventory_page_image(
                    new_box_number=new_box,
                    order_type=view_instance.order_type,
                    show_mythics_only=view_instance.show_only_mythics,
                    show_favorites_only=view_instance.show_only_favorites,
                    show_nicknames_only=view_instance.show_only_nicknames,
                    is_ascending_order=view_instance.is_ascending_order,
                    is_exclusive_mode=view_instance.is_exclusive_mode
                )
            elif hasattr(view_instance, 'avatar_board_image_factory'):
                if view_instance.open_tab == view_instance.UNLOCKED_AVATARS:
                    current_page = view_instance.avatar_board_image_factory.page_num_unlocked_avatar
                    new_page = current_page + 1 if is_next else current_page - 1
                    new_image = view_instance.avatar_board_image_factory.build_avatar_board_page_image(new_page_number=new_page, open_tab=view_instance.UNLOCKED_AVATARS)
                elif view_instance.open_tab == view_instance.AVATAR_QUESTS:
                    current_page = view_instance.avatar_board_image_factory.page_num_avatar_quests
                    new_page = current_page + 1 if is_next else current_page - 1
                    new_image = view_instance.avatar_board_image_factory.build_avatar_board_page_image(new_page_number=new_page, open_tab=view_instance.AVATAR_QUESTS)
                else:
                    return
            else:
                return

            # Update button states and send response
            view_instance.update_button_states()
            await interaction.message.edit(attachments=[convert_to_png(new_image, f'page_image.png')], view=view_instance)

    return callback

#************************************************************************************
#-----------------------------------------DROPDOWNS-------------------------------------------
#************************************************************************************
# todo these def need to be more generic
def create_page_jump_dropdown(view_instance, row=0, option_prefix="Page"):
    # Determine total pages based on view type
    if hasattr(view_instance, 'encyclopedia_image_factory'):
        total_pages = view_instance.encyclopedia_image_factory.total_pages
        current_page = view_instance.encyclopedia_image_factory.page_num
    elif hasattr(view_instance, 'encyclopedia_location_index_image_factory'):
        total_pages = view_instance.encyclopedia_location_index_image_factory.total_pages
        current_page = view_instance.encyclopedia_location_index_image_factory.page_num
    elif hasattr(view_instance, 'creature_inventory_image_factory'):
        total_pages = view_instance.max_boxes
        current_page = view_instance.creature_inventory_image_factory.current_box_num
    else:
        total_pages = 1
        current_page = 1

    options = [discord.SelectOption(label=f"{option_prefix} {i}",value=str(i), default=(i == current_page)) for i in range(1, total_pages + 1)]

    dropdown = Select(placeholder=f"Skip to {option_prefix}" if current_page == 1 else f"{option_prefix} {current_page}", options=options, min_values=1, max_values=1, row=row)
    dropdown.callback = create_generic_page_jump_callback(view_instance)
    return dropdown
def create_generic_page_jump_callback(view_instance):
    @retry_on_ssl_error(max_retries=3, delay=1)
    async def callback(interaction):
        if not await check_if_user_can_interact_with_view(interaction, view_instance.interaction_lock, view_instance.message_author.user_id):
            return

        async with view_instance.interaction_lock:
            await interaction.response.defer()

            new_page = int(interaction.data["values"][0])

            if hasattr(view_instance, 'encyclopedia_image_factory'):
                new_image = convert_to_png(view_instance.encyclopedia_image_factory.reload_image(new_page_number=new_page), 'encyclopedia_page.png')
            elif hasattr(view_instance, 'encyclopedia_location_index_image_factory'):
                new_image = convert_to_png(view_instance.encyclopedia_location_index_image_factory.reload_image(new_page_number=new_page), 'encyclopedia_location_index_page.png')
            elif hasattr(view_instance, 'creature_inventory_image_factory'):
                new_image = view_instance.reload_image(new_box_number=new_page)
            else:
                return

            # Update button states and send response
            view_instance.refresh_view()
            await interaction.message.edit(attachments=[new_image], view=view_instance)

    return callback