def call(String recordId) {
    // 1. 获取 Python 脚本并写入工作区
    def scriptText = libraryResource('feishu_audit.py')
    writeFile file: 'feishu_audit.py', text: scriptText

    // 2. 动态注入凭据
    // credentialsId 必须和你之前在 Jenkins 界面配的凭据 ID 一致
    withCredentials([
        string(credentialsId: 'FEISHU_APP_ID', variable: 'FEISHU_APP_ID'),
        string(credentialsId: 'FEISHU_APP_SECRET', variable: 'FEISHU_APP_SECRET')
    ]) {
        script {
            sh "python3 -m pip install requests --user"
            // 此时 Python 进程的环境变量里就有了：
            // - 来自 withCredentials 的 APP_ID 和 APP_SECRET
            // - 来自 Jenkins 全局配置的 TOKEN 和 TABLE_ID
            sh "python3 feishu_audit.py ${recordId}"

            // 读取审计结果环境变量文件
            if (fileExists('audit.env')) {
                def props = readProperties file: 'audit.env'
                env.IS_EMERGENCY = props['IS_EMERGENCY']
            }
        }
    }
}