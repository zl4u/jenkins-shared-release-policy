import requests
import sys
import os
import json
from datetime import datetime

# 配置从 Jenkins 注入
APP_ID = os.getenv("FEISHU_APP_ID")
APP_SECRET = os.getenv("FEISHU_APP_SECRET")
APP_TOKEN = os.getenv("FEISHU_APP_TOKEN")
TABLE_ID = os.getenv("FEISHU_TABLE_ID")

# 窗口：周四 (3) 21:30
WIN_DAY = int(os.getenv("PUBLISH_WINDOW_DAY", 3))
WIN_HOUR = int(os.getenv("PUBLISH_WINDOW_HOUR", 21))
WIN_MIN = int(os.getenv("PUBLISH_WINDOW_MINUTE", 30))

class FeishuAuditor:
    def __init__(self):
        self.token = self._get_token()

    def _get_token(self):
        url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
        r = requests.post(url, json={"app_id": APP_ID, "app_secret": APP_SECRET}, timeout=10)
        return r.json().get("tenant_access_token")

    def run(self, record_id):
        # 1. 获取飞书记录
        url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{APP_TOKEN}/tables/{TABLE_ID}/records/{record_id}"
        headers = {"Authorization": f"Bearer {self.token}"}
        res = requests.get(url, headers=headers, timeout=10).json()

        if res.get("code") != 0:
            print(f"❌ 飞书接口报错: {res.get('msg')}")
            sys.exit(1)

        fields = res["data"]["record"]["fields"]
        status = fields.get("审批状态")  # 对应多维表格中的单选列
        is_emergency = fields.get("是否紧急发布", False) # 对应复选框

        # 2. 严格日期校验
        record_ts = fields.get("发布日期", 0)
        record_date = datetime.fromtimestamp(record_ts/1000).strftime('%Y-%m-%d')
        today_date = datetime.now().strftime('%Y-%m-%d')

        # 3. 窗口判定
        now = datetime.now()
        in_window = (now.weekday() == WIN_DAY and (now.hour * 60 + now.minute) >= (WIN_HOUR * 60 + WIN_MIN))

        print(f"--- 审计执行中 ---")
        print(f"当前时间: {now.strftime('%H:%M')} | 窗口内: {'✅' if in_window else '❌'}")
        print(f"单据状态: {status} | 紧急特批: {is_emergency}")
        print(f"单据日期: {record_date} (今日: {today_date})")

        errors = []
        if record_date != today_date:
            errors.append(f"单据日期不正确。必须使用今日({today_date})新创建的单据。")
        if status != "已通过":
            errors.append("单据尚未审批通过。若是紧急发布，请联系负责人在飞书完成审批。")
        if not in_window and not is_emergency:
            errors.append(f"当前非周四{WIN_HOUR}:{WIN_MIN}窗口，且未申请紧急发布。")

        if errors:
            print("\n🚨 审计拒绝：")
            for e in errors: print(f"  - {e}")
            sys.exit(1)

        # 写入结果供 Jenkins 使用
        with open("audit.env", "w") as f:
            f.write(f"IS_EMERGENCY={str(is_emergency).lower()}\n")
        print("\n✅ 审计成功！")

if __name__ == "__main__":
    FeishuAuditor().run(sys.argv[1])