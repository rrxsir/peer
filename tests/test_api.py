from __future__ import annotations


import pytest

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from app.main import PeerReviewService, ServiceError
from app.models import ExportRequest


@pytest.fixture()
def service() -> PeerReviewService:
    return PeerReviewService()


def test_material_upload_analysis_and_export_flow(service: PeerReviewService):
    meta = {
        "applicant_name": "张伟",
        "department": "南京大学",
        "position_applied": "教授（科研岗）",
    }
    files = [("teaching_report.pdf", b"sample content")]
    upload_response = service.upload_materials(files, meta=meta)
    materials = upload_response.to_dict()["materials"]
    assert len(materials) == 1
    material_id = materials[0]["id"]

    task = service.create_task([material_id], options={"language": "zh-CN"})
    task_payload = service.get_task(task.id).to_dict()
    assert task_payload["status"] == "succeeded"
    assert task_payload["result_id"]

    result_response = service.get_result(task_payload["result_id"]).to_dict()
    assert result_response["result"]["materials"] == [material_id]
    assert result_response["result"]["summary_sections"]
    assert result_response["result"]["analysis_steps"]
    assert result_response["result"]["analysis_steps"][0]["optimizations"]

    export_status = service.create_export(ExportRequest(result_id=task_payload["result_id"], format="pdf", filename="test.pdf"))
    download_body = service.download_export(export_status.id)
    assert "结构化摘要" in download_body
    assert "分析过程" in download_body

    taxonomy = service.list_disciplines().to_dict()
    assert "人工智能" in taxonomy["disciplines"]

    version = service.get_version().to_dict()
    assert version["service"] == "peerreview-material-nlp"


def test_get_task_not_found(service: PeerReviewService):
    with pytest.raises(ServiceError) as exc:
        service.get_task("missing")
    assert exc.value.code == "not_found"
    assert "任务不存在" in exc.value.message
