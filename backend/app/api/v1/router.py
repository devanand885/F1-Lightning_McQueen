from fastapi import APIRouter

from app.api.v1 import (
    archetypes,
    circuits,
    compare,
    constructors,
    dashboard,
    driver_analytics,
    drivers,
    export,
    replay,
    search,
    seasons,
    simulator,
    strategy,
)

router = APIRouter()
router.include_router(drivers.router)
router.include_router(driver_analytics.router)
router.include_router(constructors.router)
router.include_router(circuits.router)
router.include_router(dashboard.router)
router.include_router(search.router)
router.include_router(compare.router)
router.include_router(export.router)
router.include_router(seasons.router)
router.include_router(archetypes.router)
router.include_router(simulator.router)
router.include_router(strategy.router)
router.include_router(replay.router)
