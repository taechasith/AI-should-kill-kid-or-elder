from pathlib import Path
from geosave.release_readiness import assess
def test_current_repository_is_honestly_not_release_ready():
 report=assess(Path(__file__).resolve().parents[1]); assert report['status']=='NOT_RELEASE_READY' and not report['publication_or_submission_authorized'] and report['blockers']
