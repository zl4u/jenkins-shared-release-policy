def call(Map config = [:]) {

    def tz = TimeZone.getTimeZone('Asia/Shanghai')
    def now = new Date()

    def day = now.format('u', tz) as int     // 1-7 (Mon-Sun)
    def hour = now.format('H', tz) as int    // 0-23

    // 默认规则（可集中改）
    def allowedDays = config.allowedDays ?: [2, 4]        // 周二、周四
    def forbiddenHours = config.forbiddenHours ?: [18, 21]

    // 发布日校验
    if (!allowedDays.contains(day) && !params.FORCE_RELEASE) {
        error "🚫 非发布日，仅允许周${allowedDays.join(',')} 发布"
    }

    // 时间段校验
    if (hour >= forbiddenHours[0] && hour < forbiddenHours[1] && !params.FORCE_RELEASE) {
        error "🚫 ${forbiddenHours[0]}:00-${forbiddenHours[1]}:00 禁止发布"
    }

    echo "✅ 发布规则校验通过（day=${day}, hour=${hour}）"
}
