import pygame
import settings

from level.world import FLOOR, WALL


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

    scale = 4

    offset_x = (
        settings.WIDTH
        - len(world.tiles[0]) * scale
        - settings.MINIMAP_PADDING
        - 60
    )

    offset_y = (
        settings.HEIGHT
        - len(world.tiles) * scale
        - settings.MINIMAP_PADDING
        + 30
    )

    # ===== MAP =====

    for y, row in enumerate(world.tiles):

        for x, tile in enumerate(row):

            px = offset_x + x * scale
            py = offset_y + y * scale

            color = (
                (200, 200, 200)
                if tile == FLOOR
                else (40, 40, 40)
            )

            pygame.draw.rect(
                screen,
                color,
                (px, py, scale, scale)
            )

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