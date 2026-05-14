import pytest

from mcp_manimgl_server.core import SceneManager
from mcp_manimgl_server.core.scene_manager import AnimationRecord, MobjectRecord


@pytest.fixture
def scene_manager() -> SceneManager:
    return SceneManager()


@pytest.fixture
def sample_mobject_record() -> MobjectRecord:
    return MobjectRecord(
        mobject_id="m_test",
        mobject_type="circle",
        color="#FFFFFF",
        position=[0.0, 0.0, 0.0],
        properties={"radius": 1.0},
        code_snippet="m_test = Circle(radius=1.0, color='#FFFFFF')",
    )


@pytest.fixture
def sample_animation_record() -> AnimationRecord:
    return AnimationRecord(
        animation_id="a_test",
        animation_type="fade_in",
        mobject_id="m_test",
        run_time=1.0,
        rate_func="smooth",
        properties={},
        code_snippet="self.play(FadeIn(m_test, run_time=1.0))",
    )
