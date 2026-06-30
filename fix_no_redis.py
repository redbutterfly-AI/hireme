import os

path = os.path.join("HireMeBackend", "HireMeBackend", "settings.py")
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

old_channel_layer = '''CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            'hosts': [('127.0.0.1', 6379)],
        },
    },
}'''

new_channel_layer = '''CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels.layers.InMemoryChannelLayer',
    },
}'''

if old_channel_layer in content:
    content = content.replace(old_channel_layer, new_channel_layer)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print("✅ settings.py - switched to InMemoryChannelLayer (no Redis needed)")
else:
    print("⚠️  Could not find exact CHANNEL_LAYERS block - check manually")
    print("Looking for CHANNEL_LAYERS in file...")
    if "CHANNEL_LAYERS" in content:
        idx = content.find("CHANNEL_LAYERS")
        print(content[idx:idx+300])

print("")
print("NOTE: InMemoryChannelLayer only works with a single Daphne process.")
print("This is fine for development. For production, install Redis/Memurai.")
print("")
print("Now restart backend: start_backend.ps1")
