import os
from datetime import datetime
from src.database.handlers.DatabaseHandler import get_tgommo_db_handler
from src.discord.game_features.creature_enounter.CreatureEncounterImageFactory import CreatureEncounterImageFactory
from src.resources.constants.file_paths import PROJECT_ROOT


def register_creature_encounter_tests(bot):
    @bot.command(name="TEST--generate_creature_images")
    async def generate_creature_images_test(ctx):
        """Generate encounter images for all environment creatures"""
        user_id = ctx.author.id
        message_author = get_tgommo_db_handler().get_user_profile_by_user_id(user_id)
        all_creatures = get_tgommo_db_handler().get_all_environment_creatures()

        # Create directories (4 levels up from src/discord/general/tests/)
        output_dir = os.path.join(PROJECT_ROOT, "output")
        logs_dir = os.path.join(PROJECT_ROOT, "logs")
        os.makedirs(output_dir, exist_ok=True)
        os.makedirs(logs_dir, exist_ok=True)

        current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_filename = f"test_creature_images_{current_time}.log"
        log_path = os.path.join(logs_dir, log_filename)

        status_message = await ctx.send("Starting creature image generation...")

        with open(log_path, 'w', encoding='utf-8') as log_file:
            log_file.write(f"Creature Image Generation Log - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            log_file.write("=" * 80 + "\n\n")

            for i, creature in enumerate(all_creatures):
                try:
                    current_status = f"**Processing creature {i + 1}/{len(all_creatures)}**\nGenerating: `{creature.full_name}` 💭"
                    await status_message.edit(content=current_status)

                    log_file.write(f"Generating {creature.full_name}: Processing...\n")
                    log_file.flush()

                    factory = CreatureEncounterImageFactory(
                        creature=creature,
                        environment=get_tgommo_db_handler().get_environment_by_id(creature.environment_id) if creature.environment_id != -1 else None
                    )

                    encounter_file = factory.create_encounter_image()
                    filename = f"{creature.creature_id}_{creature.full_name}_{creature.variant_name or 'default'}_{creature.environment_id}.png"
                    output_path = os.path.join(output_dir, filename)

                    with open(output_path, 'wb') as f:
                        encounter_file.fp.seek(0)
                        f.write(encounter_file.fp.read())

                    log_file.write(f"Generating {creature.creature_name}: ✅ COMPLETE\n")
                    log_file.flush()

                except Exception as e:
                    log_file.write(f"Generating {creature.creature_name}: ❌ FAILURE ({str(e)})\n")
                    log_file.flush()

            log_file.write(f"\n" + "=" * 80 + "\n")
            log_file.write(f"Generation Complete! {len(all_creatures)} creatures processed\n")
            log_file.write(f"Images saved to: {output_dir}\n")
            log_file.write(f"Log saved to: {log_path}\n")

        final_message = f"**✅ Generation Complete!**\n{len(all_creatures)} creatures processed\nImages saved to: `{output_dir}`\nLog saved to: `{log_filename}`"
        await status_message.edit(content=final_message)