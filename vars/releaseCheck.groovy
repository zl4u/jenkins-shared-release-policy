def call(Map config = [:]) {

    /* =========================
     * 1. 时间计算（明确时区）
     * ========================= */
    TimeZone tz = TimeZone.getTimeZone('Asia/Shanghai')
    Date now = new Date()

    int day  = now.format('u', tz) as int   // 1-7 (Mon-Sun)
    int hour = now.format('H', tz) as int   // 0-23

    /* =========================
     * 2. 规则配置（可集中调整）
     * ========================= */
    List<Integer> allowedDays     = (config.allowedDays ?: [2, 4]) as List<Integer>
    List<Integer> forbiddenHours  = (config.forbiddenHours ?: [18, 21]) as List<Integer>

    /* =========================
     * 3. FORCE_RELEASE 安全判断
     * ========================= */
    boolean forceRelease = (params.FORCE_RELEASE == true)

    /* =========================
     * 4. DEBUG 输出（关键）
     * ========================= */
    echo """
=========== RELEASE CHECK DEBUG ===========
now            = ${now}
timezone       = ${tz.getID()}
day (1-7)      = ${day}
hour (0-23)    = ${hour}
allowedDays    = ${allowedDays}
forbiddenHours = ${forbiddenHours}
params         = ${params}
FORCE_RELEASE  = ${params.FORCE_RELEASE}
forceRelease   = ${forceRelease}
==========================================
"""

    /* =========================
     * 5. 发布日校验
     * ========================= */
    if (!allowedDays.contains(day) && !forceRelease) {
        error "🚫 非发布日（仅允许周 ${allowedDays.join(',')}），如需发布请使用 FORCE_RELEASE"
    }

    /* =========================
     * 6. 禁止时间段校验
     * ========================= */
    if (hour >= forbiddenHours[0] && hour < forbiddenHours[1] && !forceRelease) {
        error "🚫 ${forbiddenHours[0]}:00-${forbiddenHours[1]}:00 禁止发布，如需发布请使用 FORCE_RELEASE"
    }

    echo "✅ 发布规则校验通过"
}
