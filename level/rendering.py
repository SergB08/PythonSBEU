import pygame
import settings

from level.world import FLOOR, WALL

_minimap_cache = None
_minimap_world_id = None


def draw_world(
    screen,
    world,
    floor_tiles,
    wall_tiles,
    ladder_img,
    camera_x,
    camera_y
):

    for y, row in enumerate(world.tiles):

        for x, tile in enumerate(row):

            draw_x = x * settings.TILE_SIZE - camera_x
            draw_y = y * settings.TILE_SIZE - camera_y

            # НЕ МАЛЮВАТИ ЩО ПОЗА ЕКРАНОМ
            if (
                draw_x < -settings.TILE_SIZE
                or draw_x > settings.WIDTH
                or draw_y < -settings.TILE_SIZE
                or draw_y > settings.HEIGHT
            ):
                continue

            # ===== FLOOR =====

            if tile == FLOOR:

                img = floor_tiles[
                    world.floor_variant[y][x] % len(floor_tiles)
                ]

                screen.blit(
                    img,
                    (draw_x, draw_y)
                )

            # ===== WALL =====

            elif tile == WALL:

                img = wall_tiles[0]

                screen.blit(
                    img,
                    (draw_x, draw_y)
                )

    # ===== LADDER =====

    if world.ladder_x is not None:

        ladder_draw_x = (
            world.ladder_x * settings.TILE_SIZE
            - camera_x
        )

        ladder_draw_y = (
            world.ladder_y * settings.TILE_SIZE
            - camera_y
        )

        screen.blit(
            ladder_img,
            (ladder_draw_x, ladder_draw_y)
        )


def draw_minimap(screen, world, player):
    global _minimap_cache, _minimap_world_id

    scale = settings.MINIMAP_SCALE

    map_w = len(world.tiles[0]) * scale
    map_h = len(world.tiles)    * scale

    offset_x = (
        settings.WIDTH
        - map_w
        - settings.MINIMAP_PADDING
        - 60
    )

    offset_y = (
        settings.HEIGHT
        - map_h
        - settings.MINIMAP_PADDING
        + 30
    )

    # ===== MAP (cached) =====

    if _minimap_cache is None or _minimap_world_id != id(world):
        _minimap_cache    = pygame.Surface((map_w, map_h))
        _minimap_world_id = id(world)
        for y, row in enumerate(world.tiles):
            for x, tile in enumerate(row):
                color = (200, 200, 200) if tile == FLOOR else (40, 40, 40)
                _minimap_cache.set_at((x * scale, y * scale), color)

    screen.blit(_minimap_cache, (offset_x, offset_y))

    # ===== PLAYER =====

    player_px = (
        offset_x
        + (player.world_x / settings.TILE_SIZE) * scale
    )

    player_py = (
        offset_y
        + (player.world_y / settings.TILE_SIZE) * scale
    )

    pygame.draw.circle(
        screen,
        (255, 0, 0),
        (int(player_px), int(player_py)),
        3
    )

    # ===== LADDER =====

    if world.ladder_x is not None:
        ladder_px = offset_x + world.ladder_x * scale
        ladder_py = offset_y + world.ladder_y * scale
        pygame.draw.circle(
            screen,
            (0, 255, 100),
            (int(ladder_px), int(ladder_py)),
            3
        )