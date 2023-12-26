#!/usr/bin/python3

# SPDX-FileCopyrightText: © 2022-2023 Greg Christiana <maxuser@minescript.net>
# SPDX-License-Identifier: MIT

"""Tool for renaming Java symbols between Forge and Fabric mappings.

Usage:
# Translate source with Fabric mappings to Forge mappings:
$ ./rename_minecraft_symbols.py --to_forge <$fabric_src |java-format - > $forge_src

# Translate source with Forge mappings to Fabric mappings:
$ ./rename_minecraft_symbols.py --to_fabric <$forge_src |java-format - > $fabric_src

For an implementation of java-format, see: https://github.com/google/google-java-format
"""

import re
import sys

forge_to_fabric_class_names = (
  ('com.mojang.blaze3d.platform.InputConstants', 'net.minecraft.client.util.InputUtil'),
  ('net.minecraft.client.KeyMapping', 'net.minecraft.client.option.KeyBinding'),
  ('net.minecraft.client.Minecraft', 'net.minecraft.client.MinecraftClient'),
  ('net.minecraft.client.Screenshot', 'net.minecraft.client.util.ScreenshotRecorder'),
  ('net.minecraft.client.gui.components.EditBox',
    'net.minecraft.client.gui.widget.TextFieldWidget'),
  ('net.minecraft.client.gui.screens.ChatScreen', 'net.minecraft.client.gui.screen.ChatScreen'),
  ('net.minecraft.client.gui.screens.LevelLoadingScreen',
    'net.minecraft.client.gui.screen.world.LevelLoadingScreen'),
  ('net.minecraft.client.gui.screens.ReceivingLevelScreen',
    'net.minecraft.client.gui.screen.ProgressScreen'),
  ('net.minecraft.client.gui.screens.Screen', 'net.minecraft.client.gui.screen.Screen'),
  ('net.minecraft.client.gui.screens.inventory.CreativeModeInventoryScreen',
    'net.minecraft.client.gui.screen.ingame.CreativeInventoryScreen'),
  ('net.minecraft.client.player.LocalPlayer', 'net.minecraft.client.network.ClientPlayerEntity'),
  ('net.minecraft.core.BlockPos', 'net.minecraft.util.math.BlockPos'),
  ('net.minecraft.nbt.CompoundTag', 'net.minecraft.nbt.NbtCompound'),
  ('net.minecraft.network.chat.Component.Serializer', 'net.minecraft.text.Text.Serialization'),
  ('net.minecraft.network.chat.Component', 'net.minecraft.text.Text'),
  ('net.minecraft.network.protocol.game.ServerboundPickItemPacket',
    'net.minecraft.network.packet.c2s.play.PickFromInventoryC2SPacket'),
  ('net.minecraft.world.entity.Entity', 'net.minecraft.entity.Entity'),
  ('net.minecraft.world.entity.LivingEntity', 'net.minecraft.entity.LivingEntity'),
  ('net.minecraft.world.item.ItemStack', 'net.minecraft.item.ItemStack'),
  ('net.minecraft.world.level.Level', 'net.minecraft.world.World'),
  ('net.minecraft.world.level.LevelAccessor', 'net.minecraft.world.WorldAccess'),
  ('net.minecraft.world.level.block.state.BlockState', 'net.minecraft.block.BlockState'),
  ('net.minecraft.world.level.chunk.ChunkAccess', 'net.minecraft.world.chunk.Chunk'),
  ('net.minecraft.world.level.chunk.ChunkSource', 'net.minecraft.world.chunk.ChunkManager'),
  ('net.minecraft.world.phys.BlockHitResult', 'net.minecraft.util.hit.BlockHitResult'),
  ('net.minecraft.world.phys.HitResult', 'net.minecraft.util.hit.HitResult'),
)

forge_to_fabric_member_names = (
  ('"f_95573_"', '"field_2382"'),
  ('"input"', '"chatField"'),
  ('BlockPos.MutableBlockPos', 'BlockPos.Mutable'),
  ('Component.nullToEmpty', 'Text.of'),
  ('KEYSYM.getOrCreate', 'KEYSYM.createFromCode'),
  ('KeyMapping.click', 'KeyBinding.onKeyPressed'),
  ('KeyMapping.set', 'KeyBinding.setKeyPressed'),
  ('MOUSE.getOrCreate', 'MOUSE.createFromCode'),
  ('Screenshot.grab', 'ScreenshotRecorder.saveScreenshot'),
  ('chatEditBox.getCursorPosition', 'chatEditBox.getCursor'),
  ('chatEditBox.getValue', 'chatEditBox.getText'),
  ('chatEditBox.insertText', 'chatEditBox.write'),
  ('chatEditBox.setCursorPosition', 'chatEditBox.setSelectionStart'),
  ('chatEditBox.setTextColor', 'chatEditBox.setEditableColor'),
  ('chatEditBox.setValue', 'chatEditBox.setText'),
  ('chatHud.addRecentChat', 'chatHud.addToMessageHistory'),
  ('chunkManager.getChunkNow', 'chunkManager.getWorldChunk'),
  ('chunkPos.getBlockAt', 'chunkPos.getBlockPos'),
  ('connection.send', 'connection.sendPacket'),
  ('difficulty.getSerializedName', 'difficulty.asString'),
  ('entity.getDeltaMovement', 'entity.getVelocity'),
  ('entity.getXRot', 'entity.getPitch'),
  ('entity.getYRot', 'entity.getYaw'),
  ('entity.pick', 'entity.raycast'),
  ('entity.saveWithoutId', 'entity.writeNbt'),
  ('hitResult.getDirection', 'hitResult.getSide'),
  ('inventory.getContainerSize', 'inventory.size'),
  ('inventory.getItem', 'inventory.getStack'),
  ('inventory.pickSlot', 'inventory.swapSlotWithHotbar'),
  ('inventory.selected', 'inventory.selectedSlot'),
  ('itemStack.getTag', 'itemStack.getNbt'),
  ('level.getChunkSource', 'level.getChunkManager'),
  ('minecraft.gameDirectory', 'minecraft.runDirectory'),
  ('minecraft.getConnection', 'minecraft.getNetworkHandler'),
  ('minecraft.getCurrentServer', 'minecraft.getCurrentServerEntry'),
  ('minecraft.getSingleplayerServer', 'minecraft.getServer'),
  ('minecraft.getMainRenderTarget', 'minecraft.getFramebuffer'),
  ('minecraft.gui.getChat', 'minecraft.inGameHud.getChatHud'),
  ('minecraft.level', 'minecraft.world'),
  ('minecraft.screen', 'minecraft.currentScreen'),
  ('options.keyAttack', 'options.attackKey'),
  ('options.keyDown', 'options.backKey'),
  ('options.keyDrop', 'options.dropKey'),
  ('options.keyJump', 'options.jumpKey'),
  ('options.keyLeft', 'options.leftKey'),
  ('options.keyPickItem', 'options.pickItemKey'),
  ('options.keyRight', 'options.rightKey'),
  ('options.keyShift', 'options.sneakKey'),
  ('options.keySprint', 'options.sprintKey'),
  ('options.keySwapOffhand', 'options.swapHandsKey'),
  ('options.keyUp', 'options.forwardKey'),
  ('options.keyUse', 'options.useKey'),
  ('player.connection', 'player.networkHandler'),
  ('networkHandler.sendChat', 'networkHandler.sendChatMessage'),
  ('networkHandler.sendUnsignedCommand', 'networkHandler.sendCommand'),
  ('player.getCommandSenderWorld', 'player.getEntityWorld'),
  ('player.getCommandSenderWorld', 'player.getEntityWorld'),
  ('player.getHandSlots', 'player.getHandItems'),
  ('player.getXRot', 'player.getPitch'),
  ('player.getYRot', 'player.getYaw'),
  ('player.setXRot', 'player.setPitch'),
  ('player.setYRot', 'player.setYaw'),
  ('player.moveTo', 'player.refreshPositionAndAngles'),
  ('playerWorld.dimension', 'playerWorld.getDimension'),
  ('screen.onClose', 'screen.close'),
  ('server.getWorldData', 'server.getSaveProperties'),
  ('serverData.ip', 'serverData.address'),
  ('world.entitiesForRendering', 'world.getEntities'),
  ('world.players', 'world.getPlayers'),
  ('world.getLevelData', 'world.getLevelProperties'),
  ('levelProperties.getGameTime', 'levelProperties.getTime'),
  ('levelProperties.getDayTime', 'levelProperties.getTimeOfDay'),
  ('levelProperties.getXSpawn', 'levelProperties.getSpawnX'),
  ('levelProperties.getYSpawn', 'levelProperties.getSpawnY'),
  ('levelProperties.getZSpawn', 'levelProperties.getSpawnZ'),
)

def Usage():
  print(
      "Usage: rename_minecraft_symbols.py --to_fabric|--to_forge",
      file=sys.stderr)

def CreateFullNameRewrite(before, after):
  pattern = re.compile(f"^import {before};")
  return lambda s: pattern.sub(f"import {after};", s)

def CreateSimpleNameRewrite(before, after):
  if before[0] == '"':
    pattern = re.compile(before)
    return lambda s: s if s.startswith("import ") else pattern.sub(after, s)
  else:
    pattern = re.compile(f"\\b{before}\\b")
    return lambda s: s if s.startswith("import ") else pattern.sub(after, s)

def RenameForgeToFabric():
  rewrites = []  # List of rewrite functions that take a string to rewrite.

  for forge_name, fabric_name in forge_to_fabric_member_names:
    rewrites.append(CreateSimpleNameRewrite(forge_name, fabric_name))

  for forge_name, fabric_name in forge_to_fabric_class_names:
    rewrites.append(CreateFullNameRewrite(forge_name, fabric_name))

    forge_simple_name = forge_name.split('.')[-1]
    fabric_simple_name = fabric_name.split('.')[-1]
    if forge_simple_name != fabric_simple_name:
      rewrites.append(CreateSimpleNameRewrite(forge_simple_name, fabric_simple_name))

  rewrites.append(lambda s: s.replace('/* Begin Forge only */', '/* Begin Forge only'))
  rewrites.append(lambda s: s.replace('/* End Forge only */', 'End Forge only */'))

  forge_only_pattern = re.compile(f"^( *)(.*) // Forge only$")
  rewrites.append(lambda s: forge_only_pattern.sub(r"\1// Forge only: \2", s))

  ApplyRewritesToStdin(rewrites)

def RenameFabricToForge():
  rewrites = []  # List of rewrite functions that take a string to rewrite.

  for forge_name, fabric_name in forge_to_fabric_member_names:
    rewrites.append(CreateSimpleNameRewrite(fabric_name, forge_name))

  for forge_name, fabric_name in forge_to_fabric_class_names:
    rewrites.append(CreateFullNameRewrite(fabric_name, forge_name))

    forge_simple_name = forge_name.split('.')[-1]
    fabric_simple_name = fabric_name.split('.')[-1]
    if forge_simple_name != fabric_simple_name:
      rewrites.append(CreateSimpleNameRewrite(fabric_simple_name, forge_simple_name))

  rewrites.append(lambda s: s.replace('/* Begin Forge only', '/* Begin Forge only */'))
  rewrites.append(lambda s: s.replace('End Forge only */', '/* End Forge only */'))

  forge_only_pattern = re.compile(f"^ *// Forge only: (.*)")
  rewrites.append(lambda s: forge_only_pattern.sub(r"\1 // Forge only", s))

  ApplyRewritesToStdin(rewrites)

def ApplyRewritesToStdin(rewrites):
  reading_imports = False
  commented_imports = set()
  for line in sys.stdin.readlines():
    if line.startswith('import '):
      reading_imports = True
    if not line.strip().endswith('[norewrite]'):
      for rewrite in rewrites:
        line = rewrite(line)

    if reading_imports and not re.match('(import |// (Fabric|Forge) only: import )', line):
      reading_imports = False
      for commented_import in sorted(commented_imports):
        print(commented_import, end="")

    if re.match('// (Fabric|Forge) only:', line):
      commented_imports.add(line)
    else:
      print(line, end="")


def main(argv):
  if len(argv) != 1:
    Usage()
  elif argv[0] == "--to_fabric":
    RenameForgeToFabric()
  elif argv[0] == "--to_forge":
    RenameFabricToForge()
  else:
    Usage()

if __name__ == "__main__":
  main(sys.argv[1:])
