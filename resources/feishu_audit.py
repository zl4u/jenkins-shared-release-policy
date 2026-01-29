import os
import sys
import json
import urllib.request
from datetime import datetime

def post_json(url, data, token=None):
    req = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'), method='POST')
    req.add_header('Content-Type', 'application/json; charset=utf-8')
    if token: req.add_header('Authorization', f'Bearer {token}')
    with urllib.request.urlopen(req) as f: return json.loads(f.read().decode('utf-8'))

def get_json(url, token):
    req = urllib.request.Request(url, method='GET')
    req.add_header('Authorization', f'Bearer {token}')
    with urllib.request.urlopen(req) as f: return json.loads(f.read().decode('utf-8'))

def run():
    # 获取 Jenkins 传入的参数
    record_id = sys.argv[1]
    expected_service = sys.argv[2]

    # 获取 Jenkins 凭据注入的环境变量
    app_id, app_secret = os.getenv("FEISHU_APP_ID"), os.getenv("FEISHU_APP_SECRET")
    app_token, table_id = os.getenv("FEISHU_APP_TOKEN"), os.getenv("FEISHU_TABLE_ID")

    try:
        # A. 获取 Token
        token = post_json("https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
                          {"app_id": app_id, "app_secret": app_secret})["tenant_access_token"]

        # B. 获取记录
        url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/records/{record_id}"
        fields = get_json(url, token)["data"]["record"]["fields"]

        # C. 核心对账
        feishu_services = fields.get("服务", [])
        status = fields.get("审批状态")
        is_emergency = str(fields.get("是否紧急发布", "false")).lower() == "true"

        # 转换日期
        publish_date_raw = fields.get("日期")
        today = datetime.now().strftime('%Y-%m-%d')
        publish_date_str = datetime.fromtimestamp(publish_date_raw / 1000).strftime('%Y-%m-%d') if isinstance(publish_date_raw, int) else str(publish_date_raw)[:10]

        # D. 判定
        is_service_matched = any(str(s).strip().lower() == expected_service.lower() for s in feishu_services)

        print(f"--- 审计对账 ---")
        print(f"项目: {expected_service} | 飞书勾选: {feishu_services} | 状态: {status} | 日期: {publish_date_str}")

        if not is_service_matched:
            print(f"❌ 审计失败：服务名不匹配！")
            sys.exit(1)
        if status != "已通过":
            print(f"❌ 审计失败：单据未审批通过！")
            sys.exit(1)
        if publish_date_str != today:
            print(f"❌ 审计失败：单据已过期！")
            sys.exit(1)

        # 成功通过，标记环境
        with open("audit.env", "w") as f:
            f.write(f"IS_EMERGENCY={is_emergency}")
        print("✅ 审计成功！")

    except Exception as e:
        print(f"💥 异常: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run()