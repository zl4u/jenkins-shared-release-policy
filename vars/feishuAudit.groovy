def call(String recordId) {
    // 提取脚本
    def scriptText = libraryResource('feishu_audit.py')
    writeFile file: 'feishu_audit.py', text: scriptText

    withCredentials([
        string(credentialsId: 'FEISHU_APP_ID', variable: 'FEISHU_APP_ID'),
        string(credentialsId: 'FEISHU_APP_SECRET', variable: 'FEISHU_APP_SECRET')
    ]) {
        script {
            // 直接运行 Python，不使用 pip
            sh "python3 feishu_audit.py ${recordId}"

            // 用简单的 shell 命令读取结果，绕过 readJSON 插件
            def emergencyStr = sh(script: "grep 'IS_EMERGENCY' audit.env | cut -d'=' -f2", returnStdout: true).trim()
            env.IS_EMERGENCY = emergencyStr
        }
    }
}