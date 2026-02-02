def call(String recordId) {
    // 1. 获取分支名称（复用你 Jenkinsfile 里的逻辑）
    def branchName = env.BRANCH_NAME ?: env.GIT_BRANCH ?: 'master'
    branchName = branchName.replaceAll('origin/', '').replaceAll('.*/', '')

    // 2. 获取环境名称
    def envName = env.ENV_NAME // 例如 'prod'

    // 3. 核心判定逻辑
    if (envName == 'prod') {
        echo "🛡️ 检测到正式环境 (PROD) 发布，启动强制审计流程..."

        // 安全红线：PROD 环境必须是 master 分支
        // if (branchName != 'master') {
        //     error "🚨 流程拦截：正式环境 (PROD) 仅允许从 master 分支发布！当前分支为: ${branchName}"
        // }

        // 参数校验：PROD 环境必须输入 Record ID
        if (!recordId || recordId.trim() == "") {
            error "🚨 流程拦截：正式环境 (PROD) 发布必须输入飞书 Record ID！"
        }

        // 4. 执行 Python 审计脚本
        script {
            def scriptText = libraryResource('feishu_audit.py')
            writeFile file: 'feishu_audit.py', text: scriptText

            withCredentials([
                string(credentialsId: 'FEISHU_APP_ID', variable: 'FEISHU_APP_ID'),
                string(credentialsId: 'FEISHU_APP_SECRET', variable: 'FEISHU_APP_SECRET'),
                // string(credentialsId: 'FEISHU_APP_TOKEN', variable: 'FEISHU_APP_TOKEN'),
                // string(credentialsId: 'FEISHU_TABLE_ID', variable: 'FEISHU_TABLE_ID')
            ]) {
                sh "python3 feishu_audit.py ${recordId} ${env.PROJECT_NAME}"
            }
        }
    } else {
        // 非 PROD 环境逻辑
        echo "ℹ️  当前环境为 [${envName}]，跳过自动化审计及分支强校验。"
    }
}