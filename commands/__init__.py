# Create an empty __init__.py file in the commands directory
init_py_path = "/mnt/data/discord_bot_files/discord-kite-bot/commands/__init__.py"

with open(init_py_path, "w", encoding="utf-8") as file:
    file.write("# This file marks the 'commands' directory as a package.\n")

# Confirm that the file now exists
os.path.exists(init_py_path)
