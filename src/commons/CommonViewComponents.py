import discord


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