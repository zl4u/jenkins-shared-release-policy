import os
import sys
import json
import urllib.request
import urllib.parse
from datetime import datetime

def post_json(url, data, token=None):
    req = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'), method='POST')
    req.add_header('Content-Type', 'application/json; charset=utf-8')
    if token:
        req.add_header('Authorization', f'Bearer {token}')
    with urllib.request.urlopen(req) as f:
        return json.loads(f.read().decode('utf-8'))

def get_json(url, token):
    req = urllib.request.Request(url, method='GET')
    req.add_header('Authorization', f'Bearer {token}')
    with urllib.request.urlopen(req) as f:
        return json.loads(f.read().decode('utf-8'))

def run():
    record_id = sys.argv[1]
    app_id = os.getenv("FEISHU_APP_ID")
    app_secret = os.getenv("FEISHU_APP_SECRET")
    app_token = os.getenv("FEISHU_APP_TOKEN")
    table_id = os.getenv("FEISHU_TABLE_ID")

    try:
        # 1. 获取 Token
        token_url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
        token_res = post_json(token_url, {"app_id": app_id, "app_secret": app_secret})
        token = token_res.get("tenant_access_token")

        # 2. 获取记录内容
        record_url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/records/{record_id}"
        res = get_json(record_url, token)

        if res.get("code") != 0:
            print(f"🚨 飞书接口错误: {res.get('msg')}")
            sys.exit(1)

        fields = res["data"]["record"]["fields"]
        status = fields.get("审批状态")
        is_emergency = fields.get("是否紧急", False)

        print(f"--- 审计结果 ---")
        print(f"单据状态: {status} | 是否紧急: {is_emergency}")

        if status == "已通过":
            # 审计通过，写入标记文件
            with open("audit.env", "w") as f:
                f.write(f"IS_EMERGENCY={str(is_emergency).lower()}")
            print("✅ 审计通过")
        else:
            print("❌ 审计拒绝：单据未审批通过")
            sys.exit(1)

    except Exception as e:
        print(f"💥 运行异常: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    run()