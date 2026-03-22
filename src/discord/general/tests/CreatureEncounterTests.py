import os

from src.commons.logs.LogHandler import LogHandler
from src.database.handlers.DatabaseHandler import get_tgommo_db_handler
from src.discord.game_features.creature_enounter.CreatureEncounterImageFactory import CreatureEncounterImageFactory
from src.discord.objects.CreatureRarity import MYTHICAL
from src.resources.constants.file_paths import PROJECT_ROOT, LOGS_DIR, OUTPUT_DIR


"""Generate encounter images for all environment creatures"""
def register_creature_encounter_tests(bot):
    @bot.command(name="TEST--generate_creature_encounter_images")
    async def generate_creature_images_test(ctx, environment_id: int = None, mythical: bool = False):
        user_id = ctx.author.id
        message_author = get_tgommo_db_handler().get_user_profile_by_user_id(user_id)

        # Filter creatures based on parameters
        all_creatures = get_tgommo_db_handler().get_creatures_for_environment_by_environment_id(environment_id=environment_id) if environment_id else get_tgommo_db_handler().get_all_environment_creatures()

        status_message = await ctx.send("Starting creature image generation...")

        with LogHandler("TEST--generate_creature_encounter_images") as logger:
            for i, creature in enumerate(all_creatures):
                try:
                    # update log with current creature being processed
                    logger.write(f"Generating {creature.full_name}: Processing...\n")

                    # update discord message with progress
                    current_status = f"**Processing creature {i + 1}/{len(all_creatures)}**\nGenerating: `{creature.full_name}` 💭"
                    await status_message.edit(content=current_status)

                    # Generate the encounter image for the creature
                    if mythical:
                        creature.set_creature_rarity(MYTHICAL)

                    encounter_image_factory = CreatureEncounterImageFactory(creature=creature, environment=get_tgommo_db_handler().get_environment_by_id(creature.environment_id) if creature.environment_id != -1 else None)
                    encounter_file = encounter_image_factory.create_encounter_image()

                    # Save the image to the output directory with a unique filename
                    mythical_suffix = "_mythical" if mythical else ""
                    encounter_image_filename = f"{creature.creature_id}_{creature.full_name}_{creature.variant_name or 'default'}_{creature.environment_id}{mythical_suffix}.png"
                    encounter_image = os.path.join(OUTPUT_DIR, encounter_image_filename)
                    with open(encounter_image, 'wb') as f:
                        encounter_file.fp.seek(0)
                        f.write(encounter_file.fp.read())

                    logger.write(f"Generating {creature.full_name}: ✅ COMPLETE\n")
                except Exception as e:
                    logger.write(f"Generating {creature.full_name}: ❌ FAILURE ({str(e)})\n")

            # finish log with summary of results
            logger.write(f"\n" + "=" * 80 + "\n")
            logger.write(f"Generation Complete! {len(all_creatures)} creatures processed\n")

        # update discord message with final status and log location
        await status_message.edit(content=f"**✅ Generation Complete!**\n{len(all_creatures)} creatures processed\nImages saved to: `{OUTPUT_DIR}`\nLog saved to: `{os.path.basename(logger.log_path)}`")