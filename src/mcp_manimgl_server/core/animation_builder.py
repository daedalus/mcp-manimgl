from __future__ import annotations

from typing import Any

from mcp_manimgl_server.core.scene_manager import AnimationRecord


class AnimationBuilder:
    RATE_FUNCTIONS = {
        "smooth",
        "linear",
        "ease_in_sine",
        "ease_out_sine",
        "ease_in_out_sine",
        "ease_in_quad",
        "ease_out_quad",
        "ease_in_out_quad",
        "ease_in_cubic",
        "ease_out_cubic",
        "ease_in_out_cubic",
        "ease_in_quart",
        "ease_out_quart",
        "ease_in_out_quart",
        "ease_in_quint",
        "ease_out_quint",
        "ease_in_out_quint",
        "ease_in_expo",
        "ease_out_expo",
        "ease_in_out_expo",
        "ease_in_circ",
        "ease_out_circ",
        "ease_in_out_circ",
        "ease_in_elastic",
        "ease_out_elastic",
        "ease_in_out_elastic",
        "ease_in_back",
        "ease_out_back",
        "ease_in_out_back",
        "ease_in_bounce",
        "ease_out_bounce",
        "ease_in_out_bounce",
        "there_and_back",
        "there_and_back_with_pause",
        "running_start",
        "wiggle",
    }

    @staticmethod
    def _next_id() -> str:
        import uuid

        return f"a_{uuid.uuid4().hex[:8]}"

    @staticmethod
    def _rate_func_str(rf: str) -> str:
        return rf

    @classmethod
    def animate_transform(
        cls,
        mobject_id: str,
        target_mobject_type: str | None = None,
        target_config: dict[str, Any] | None = None,
        run_time: float = 1.0,
        rate_func: str = "smooth",
    ) -> AnimationRecord:
        aid = cls._next_id()
        if target_mobject_type:
            config = target_config or {}
            color = config.get("color", "RED")
            fill_opacity = config.get("fill_opacity", 0.0)
            code = (
                f"target = {target_mobject_type.capitalize()}(color='{color}', "
                f"fill_opacity={fill_opacity})\n"
                f"self.play(Transform({mobject_id}, target, "
                f"run_time={run_time}, rate_func={rate_func}))"
            )
        else:
            code = (
                f"self.play({mobject_id}.animate, "
                f"run_time={run_time}, rate_func={rate_func})"
            )
        return AnimationRecord(
            animation_id=aid,
            animation_type="transform",
            mobject_id=mobject_id,
            run_time=run_time,
            rate_func=rate_func,
            properties={
                "target_type": target_mobject_type,
                "target_config": target_config or {},
            },
            code_snippet=code,
        )

    @classmethod
    def animate_fade_in(
        cls,
        mobject_id: str,
        run_time: float = 1.0,
        shift_direction: list[float] | None = None,
    ) -> AnimationRecord:
        aid = cls._next_id()
        if shift_direction:
            sd = f"np.array([{shift_direction[0]}, {shift_direction[1]}, "
            sd += f"{shift_direction[2] if len(shift_direction) > 2 else 0.0}])"
            code = f"self.play(FadeIn({mobject_id}, {sd}, run_time={run_time}))"
        else:
            code = f"self.play(FadeIn({mobject_id}, run_time={run_time}))"
        return AnimationRecord(
            animation_id=aid,
            animation_type="fade_in",
            mobject_id=mobject_id,
            run_time=run_time,
            rate_func="smooth",
            properties={"shift_direction": shift_direction},
            code_snippet=code,
        )

    @classmethod
    def animate_fade_out(
        cls, mobject_id: str, run_time: float = 1.0
    ) -> AnimationRecord:
        aid = cls._next_id()
        code = f"self.play(FadeOut({mobject_id}, run_time={run_time}))"
        return AnimationRecord(
            animation_id=aid,
            animation_type="fade_out",
            mobject_id=mobject_id,
            run_time=run_time,
            rate_func="smooth",
            properties={},
            code_snippet=code,
        )

    @classmethod
    def animate_grow(
        cls, mobject_id: str, grow_type: str = "center", run_time: float = 1.0
    ) -> AnimationRecord:
        aid = cls._next_id()
        grow_map = {
            "center": "GrowFromCenter",
            "point": "GrowFromPoint",
            "edge": "GrowFromEdge",
            "arrow": "GrowArrow",
        }
        anim_class = grow_map.get(grow_type, "GrowFromCenter")
        code = f"self.play({anim_class}({mobject_id}, run_time={run_time}))"
        return AnimationRecord(
            animation_id=aid,
            animation_type="grow",
            mobject_id=mobject_id,
            run_time=run_time,
            rate_func="smooth",
            properties={"grow_type": grow_type},
            code_snippet=code,
        )

    @classmethod
    def animate_rotate(
        cls,
        mobject_id: str,
        angle: float | None = None,
        axis: list[float] | None = None,
        run_time: float = 1.0,
    ) -> AnimationRecord:
        aid = cls._next_id()
        angle_str = angle if angle is not None else "2 * PI"
        if axis:
            ax = (
                f"np.array([{axis[0]}, {axis[1]}, {axis[2] if len(axis) > 2 else 0.0}])"
            )
            code = (
                f"self.play(Rotate({mobject_id}, angle={angle_str}, "
                f"axis={ax}, run_time={run_time}))"
            )
        else:
            code = (
                f"self.play(Rotate({mobject_id}, angle={angle_str}, "
                f"run_time={run_time}))"
            )
        return AnimationRecord(
            animation_id=aid,
            animation_type="rotate",
            mobject_id=mobject_id,
            run_time=run_time,
            rate_func="smooth",
            properties={"angle": angle, "axis": axis},
            code_snippet=code,
        )

    @classmethod
    def animate_scale(
        cls, mobject_id: str, scale_factor: float, run_time: float = 1.0
    ) -> AnimationRecord:
        aid = cls._next_id()
        code = (
            f"self.play(ScaleInPlace({mobject_id}, {scale_factor}, "
            f"run_time={run_time}))"
        )
        return AnimationRecord(
            animation_id=aid,
            animation_type="scale",
            mobject_id=mobject_id,
            run_time=run_time,
            rate_func="smooth",
            properties={"scale_factor": scale_factor},
            code_snippet=code,
        )

    @classmethod
    def animate_shift(
        cls, mobject_id: str, vector: list[float], run_time: float = 1.0
    ) -> AnimationRecord:
        aid = cls._next_id()
        v = f"np.array([{vector[0]}, {vector[1]}, {vector[2] if len(vector) > 2 else 0.0}])"
        code = f"self.play(ApplyMethod({mobject_id}.shift, {v}, run_time={run_time}))"
        return AnimationRecord(
            animation_id=aid,
            animation_type="shift",
            mobject_id=mobject_id,
            run_time=run_time,
            rate_func="smooth",
            properties={"vector": vector},
            code_snippet=code,
        )

    @classmethod
    def animate_indicate(
        cls, mobject_id: str, run_time: float = 0.5
    ) -> AnimationRecord:
        aid = cls._next_id()
        code = f"self.play(Indicate({mobject_id}, run_time={run_time}))"
        return AnimationRecord(
            animation_id=aid,
            animation_type="indicate",
            mobject_id=mobject_id,
            run_time=run_time,
            rate_func="smooth",
            properties={},
            code_snippet=code,
        )

    @classmethod
    def animate_write(cls, mobject_id: str, run_time: float = 3.0) -> AnimationRecord:
        aid = cls._next_id()
        code = f"self.play(Write({mobject_id}, run_time={run_time}))"
        return AnimationRecord(
            animation_id=aid,
            animation_type="write",
            mobject_id=mobject_id,
            run_time=run_time,
            rate_func="smooth",
            properties={},
            code_snippet=code,
        )

    @classmethod
    def animate_set_color(
        cls, mobject_id: str, color: str, run_time: float = 1.0
    ) -> AnimationRecord:
        aid = cls._next_id()
        code = (
            f"self.play({mobject_id}.animate.set_color('{color}'), run_time={run_time})"
        )
        return AnimationRecord(
            animation_id=aid,
            animation_type="set_color",
            mobject_id=mobject_id,
            run_time=run_time,
            rate_func="smooth",
            properties={"color": color},
            code_snippet=code,
        )

    @classmethod
    def animate_move_along_path(
        cls,
        mobject_id: str,
        path_type: str = "circle",
        path_config: dict[str, Any] | None = None,
        run_time: float = 3.0,
    ) -> AnimationRecord:
        aid = cls._next_id()
        config = path_config or {}
        if path_type == "circle":
            code = (
                f"path = Circle(radius={config.get('radius', 2.0)})\n"
                f"self.play(MoveAlongPath({mobject_id}, path, "
                f"run_time={run_time}))"
            )
        elif path_type == "line":
            end = config.get("end", [3, 0, 0])
            e = f"np.array([{end[0]}, {end[1]}, {end[2] if len(end) > 2 else 0.0}])"
            code = (
                f"path = Line(ORIGIN, {e})\n"
                f"self.play(MoveAlongPath({mobject_id}, path, "
                f"run_time={run_time}))"
            )
        else:
            code = (
                f"self.play(MoveAlongPath({mobject_id}, {path_type}, "
                f"run_time={run_time}))"
            )
        return AnimationRecord(
            animation_id=aid,
            animation_type="move_along_path",
            mobject_id=mobject_id,
            run_time=run_time,
            rate_func="smooth",
            properties={"path_type": path_type, "path_config": config},
            code_snippet=code,
        )

    @classmethod
    def animate_group(
        cls,
        animation_data: list[dict[str, Any]],
        group_type: str = "animation_group",
        run_time: float = 1.0,
    ) -> AnimationRecord:
        aid = cls._next_id()

        group_map = {
            "animation_group": "AnimationGroup",
            "succession": "Succession",
            "lagged_start": "LaggedStart",
        }
        group_class = group_map.get(group_type, "AnimationGroup")

        code_lines = []
        for i, ad in enumerate(animation_data):
            ref = f"anim_{i}"
            atype = ad.get("type", "FadeIn")
            mob_id = ad.get("mobject_id", "")
            extra = ad.get("config", {})
            extra_str = ", ".join(f"{k}={v}" for k, v in extra.items())
            extra_str = f", {extra_str}" if extra_str else ""
            code_lines.append(f"{ref} = {atype}({mob_id}{extra_str})")
        refs_str = ", ".join(f"anim_{i}" for i in range(len(animation_data)))
        code_lines.append(f"self.play({group_class}({refs_str}), run_time={run_time})")
        code = "\n".join(code_lines)

        return AnimationRecord(
            animation_id=aid,
            animation_type="group",
            mobject_id="",
            run_time=run_time,
            rate_func="smooth",
            properties={
                "group_type": group_type,
                "animation_count": len(animation_data),
            },
            code_snippet=code,
        )
