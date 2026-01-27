def call(String recordId) {
    withCredentials([
        string(credentialsId: 'FEISHU_APP_ID', variable: 'APP_ID'),
        string(credentialsId: 'FEISHU_APP_SECRET', variable: 'APP_SECRET')
    ]) {
        script {
            // 1. 获取 Tenant Access Token
            def tokenJson = sh(script: """
                curl -s -X POST "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal" \
                -H "Content-Type: application/json; charset=utf-8" \
                -d '{"app_id":"${APP_ID}","app_secret":"${APP_SECRET}"}'
            """, returnStdout: true).trim()

            def token = readJSON(text: tokenJson).tenant_access_token

            // 2. 获取多维表格记录
            def recordJson = sh(script: """
                curl -s -H "Authorization: Bearer ${token}" \
                "https://open.feishu.cn/open-apis/bitable/v1/apps/${env.FEISHU_APP_TOKEN}/tables/${env.FEISHU_APP_ID}/records/${recordId}"
            """, returnStdout: true).trim()

            def data = readJSON(text: recordJson)
            def fields = data.data.record.fields

            // 3. 逻辑判定
            def status = fields['审批状态']
            if (status != '已通过') {
                error "🚨 审计拒绝：飞书单据状态为 [${status}]，请审批通过后再发布！"
            }

            env.IS_EMERGENCY = fields['是否紧急'] ?: 'false'
            echo "✅ 审计成功！当前紧急状态: ${env.IS_EMERGENCY}"
        }
    }
}