# Honeypot Incident Report — static_real_ssh_hydra_multi_user

**Generated:** 2026-06-01 17:59:13 UTC
**Blueprint:** ssh_bruteforce
**Mode:** STATIC BASELINE
**Session Start:** 2026-06-01T17:57:01
**Total Steps:** 13
**Host Ports:** {"22": "37791"}

---

## Attack Summary

| Field | Value |
|---|---|
| Session ID | static_real_ssh_hydra_multi_user |
| Blueprint Deployed | ssh_bruteforce |
| Mode | STATIC BASELINE |
| Final Engagement Score | 1063 |
| Total Events | 556 |
| Behavior Switches | 0 |

---

## Session Timeline

| # | Timestamp | Event Type | Detail | Score Δ |
|---|---|---|---|---|
| 1 | 2026-06-01T17:57:06 | connection | | 1 |
| 2 | 2026-06-01T17:57:06 | connection | | 1 |
| 3 | 2026-06-01T17:57:06 | connection | | 1 |
| 4 | 2026-06-01T17:57:06 | connection | | 1 |
| 5 | 2026-06-01T17:57:06 | connection | | 1 |
| 6 | 2026-06-01T17:57:06 | login_attempt | user=root | 2 |
| 7 | 2026-06-01T17:57:06 | login_attempt | user=root | 2 |
| 8 | 2026-06-01T17:57:06 | login_attempt | user=root | 2 |
| 9 | 2026-06-01T17:57:06 | login_attempt | user=root | 2 |
| 10 | 2026-06-01T17:57:06 | connection | | 1 |
| 11 | 2026-06-01T17:57:06 | connection | | 1 |
| 12 | 2026-06-01T17:57:06 | connection | | 1 |
| 13 | 2026-06-01T17:57:06 | login_attempt | user=admin | 2 |
| 14 | 2026-06-01T17:57:06 | login_attempt | user=admin | 2 |
| 15 | 2026-06-01T17:57:06 | login_attempt | user=admin | 2 |
| 16 | 2026-06-01T17:57:07 | connection | | 1 |
| 17 | 2026-06-01T17:57:07 | login_attempt | user=admin | 2 |
| 18 | 2026-06-01T17:57:07 | login_attempt | user=admin | 2 |
| 19 | 2026-06-01T17:57:07 | login_attempt | user=admin | 2 |
| 20 | 2026-06-01T17:57:07 | login_attempt | user=admin | 2 |
| 21 | 2026-06-01T17:57:08 | login_attempt | user=admin | 2 |
| 22 | 2026-06-01T17:57:08 | login_attempt | user=admin | 2 |
| 23 | 2026-06-01T17:57:08 | login_attempt | user=admin | 2 |
| 24 | 2026-06-01T17:57:08 | login_attempt | user=admin | 2 |
| 25 | 2026-06-01T17:57:09 | login_attempt | user=admin | 2 |
| 26 | 2026-06-01T17:57:09 | login_attempt | user=admin | 2 |
| 27 | 2026-06-01T17:57:09 | login_attempt | user=admin | 2 |
| 28 | 2026-06-01T17:57:09 | login_attempt | user=admin | 2 |
| 29 | 2026-06-01T17:57:10 | login_attempt | user=admin | 2 |
| 30 | 2026-06-01T17:57:10 | login_attempt | user=admin | 2 |
| 31 | 2026-06-01T17:57:10 | login_attempt | user=admin | 2 |
| 32 | 2026-06-01T17:57:10 | login_attempt | user=admin | 2 |
| 33 | 2026-06-01T17:57:11 | login_attempt | user=admin | 2 |
| 34 | 2026-06-01T17:57:11 | login_attempt | user=admin | 2 |
| 35 | 2026-06-01T17:57:11 | login_attempt | user=admin | 2 |
| 36 | 2026-06-01T17:57:11 | login_attempt | user=admin | 2 |
| 37 | 2026-06-01T17:57:12 | login_attempt | user=admin | 2 |
| 38 | 2026-06-01T17:57:12 | login_attempt | user=admin | 2 |
| 39 | 2026-06-01T17:57:12 | login_attempt | user=admin | 2 |
| 40 | 2026-06-01T17:57:12 | login_attempt | user=admin | 2 |
| 41 | 2026-06-01T17:57:13 | login_attempt | user=admin | 2 |
| 42 | 2026-06-01T17:57:13 | login_attempt | user=admin | 2 |
| 43 | 2026-06-01T17:57:13 | login_attempt | user=admin | 2 |
| 44 | 2026-06-01T17:57:13 | login_attempt | user=admin | 2 |
| 45 | 2026-06-01T17:57:14 | login_attempt | user=admin | 2 |
| 46 | 2026-06-01T17:57:14 | login_attempt | user=admin | 2 |
| 47 | 2026-06-01T17:57:14 | login_attempt | user=admin | 2 |
| 48 | 2026-06-01T17:57:14 | login_attempt | user=admin | 2 |
| 49 | 2026-06-01T17:57:15 | login_attempt | user=admin | 2 |
| 50 | 2026-06-01T17:57:15 | login_attempt | user=admin | 2 |
| 51 | 2026-06-01T17:57:15 | login_attempt | user=admin | 2 |
| 52 | 2026-06-01T17:57:15 | login_attempt | user=admin | 2 |
| 53 | 2026-06-01T17:57:16 | login_attempt | user=admin | 2 |
| 54 | 2026-06-01T17:57:16 | login_attempt | user=admin | 2 |
| 55 | 2026-06-01T17:57:16 | login_attempt | user=admin | 2 |
| 56 | 2026-06-01T17:57:16 | login_attempt | user=admin | 2 |
| 57 | 2026-06-01T17:57:17 | login_attempt | user=admin | 2 |
| 58 | 2026-06-01T17:57:17 | login_attempt | user=admin | 2 |
| 59 | 2026-06-01T17:57:17 | login_attempt | user=admin | 2 |
| 60 | 2026-06-01T17:57:17 | login_attempt | user=admin | 2 |
| 61 | 2026-06-01T17:57:18 | login_attempt | user=admin | 2 |
| 62 | 2026-06-01T17:57:18 | login_attempt | user=admin | 2 |
| 63 | 2026-06-01T17:57:18 | login_attempt | user=admin | 2 |
| 64 | 2026-06-01T17:57:18 | login_attempt | user=admin | 2 |
| 65 | 2026-06-01T17:57:19 | login_attempt | user=admin | 2 |
| 66 | 2026-06-01T17:57:19 | login_attempt | user=admin | 2 |
| 67 | 2026-06-01T17:57:19 | login_attempt | user=admin | 2 |
| 68 | 2026-06-01T17:57:19 | login_attempt | user=admin | 2 |
| 69 | 2026-06-01T17:57:20 | login_attempt | user=admin | 2 |
| 70 | 2026-06-01T17:57:20 | login_attempt | user=admin | 2 |
| 71 | 2026-06-01T17:57:20 | login_attempt | user=admin | 2 |
| 72 | 2026-06-01T17:57:20 | login_attempt | user=admin | 2 |
| 73 | 2026-06-01T17:57:21 | login_attempt | user=admin | 2 |
| 74 | 2026-06-01T17:57:21 | login_attempt | user=admin | 2 |
| 75 | 2026-06-01T17:57:21 | login_attempt | user=admin | 2 |
| 76 | 2026-06-01T17:57:21 | login_attempt | user=admin | 2 |
| 77 | 2026-06-01T17:57:22 | login_attempt | user=admin | 2 |
| 78 | 2026-06-01T17:57:22 | login_attempt | user=admin | 2 |
| 79 | 2026-06-01T17:57:22 | login_attempt | user=admin | 2 |
| 80 | 2026-06-01T17:57:22 | login_attempt | user=admin | 2 |
| 81 | 2026-06-01T17:57:23 | login_attempt | user=admin | 2 |
| 82 | 2026-06-01T17:57:23 | login_attempt | user=admin | 2 |
| 83 | 2026-06-01T17:57:23 | login_attempt | user=admin | 2 |
| 84 | 2026-06-01T17:57:23 | login_attempt | user=admin | 2 |
| 85 | 2026-06-01T17:57:24 | login_attempt | user=admin | 2 |
| 86 | 2026-06-01T17:57:24 | login_attempt | user=admin | 2 |
| 87 | 2026-06-01T17:57:24 | login_attempt | user=admin | 2 |
| 88 | 2026-06-01T17:57:24 | login_attempt | user=admin | 2 |
| 89 | 2026-06-01T17:57:25 | login_attempt | user=admin | 2 |
| 90 | 2026-06-01T17:57:25 | login_attempt | user=admin | 2 |
| 91 | 2026-06-01T17:57:25 | login_attempt | user=admin | 2 |
| 92 | 2026-06-01T17:57:25 | login_attempt | user=admin | 2 |
| 93 | 2026-06-01T17:57:26 | login_attempt | user=admin | 2 |
| 94 | 2026-06-01T17:57:26 | login_attempt | user=admin | 2 |
| 95 | 2026-06-01T17:57:26 | login_attempt | user=admin | 2 |
| 96 | 2026-06-01T17:57:26 | login_attempt | user=admin | 2 |
| 97 | 2026-06-01T17:57:27 | login_attempt | user=admin | 2 |
| 98 | 2026-06-01T17:57:27 | connection | | 1 |
| 99 | 2026-06-01T17:57:27 | connection | | 1 |
| 100 | 2026-06-01T17:57:27 | connection | | 1 |
| 101 | 2026-06-01T17:57:27 | login_attempt | user=admin | 2 |
| 102 | 2026-06-01T17:57:27 | login_attempt | user=admin | 2 |
| 103 | 2026-06-01T17:57:27 | login_attempt | user=admin | 2 |
| 104 | 2026-06-01T17:57:28 | connection | | 1 |
| 105 | 2026-06-01T17:57:28 | login_attempt | user=admin | 2 |
| 106 | 2026-06-01T17:57:28 | login_attempt | user=admin | 2 |
| 107 | 2026-06-01T17:57:28 | login_attempt | user=admin | 2 |
| 108 | 2026-06-01T17:57:28 | login_attempt | user=admin | 2 |
| 109 | 2026-06-01T17:57:29 | login_attempt | user=admin | 2 |
| 110 | 2026-06-01T17:57:29 | login_attempt | user=admin | 2 |
| 111 | 2026-06-01T17:57:29 | login_attempt | user=admin | 2 |
| 112 | 2026-06-01T17:57:29 | login_attempt | user=admin | 2 |
| 113 | 2026-06-01T17:57:30 | login_attempt | user=admin | 2 |
| 114 | 2026-06-01T17:57:30 | login_attempt | user=admin | 2 |
| 115 | 2026-06-01T17:57:30 | connection | | 1 |
| 116 | 2026-06-01T17:57:30 | connection | | 1 |
| 117 | 2026-06-01T17:57:31 | login_attempt | user=backup | 2 |
| 118 | 2026-06-01T17:57:31 | login_attempt | user=backup | 2 |
| 119 | 2026-06-01T17:57:31 | connection | | 1 |
| 120 | 2026-06-01T17:57:31 | connection | | 1 |
| 121 | 2026-06-01T17:57:32 | login_attempt | user=backup | 2 |
| 122 | 2026-06-01T17:57:32 | login_attempt | user=backup | 2 |
| 123 | 2026-06-01T17:57:32 | login_attempt | user=backup | 2 |
| 124 | 2026-06-01T17:57:32 | login_attempt | user=backup | 2 |
| 125 | 2026-06-01T17:57:33 | login_attempt | user=backup | 2 |
| 126 | 2026-06-01T17:57:33 | login_attempt | user=backup | 2 |
| 127 | 2026-06-01T17:57:33 | login_attempt | user=backup | 2 |
| 128 | 2026-06-01T17:57:33 | login_attempt | user=backup | 2 |
| 129 | 2026-06-01T17:57:34 | login_attempt | user=backup | 2 |
| 130 | 2026-06-01T17:57:34 | login_attempt | user=backup | 2 |
| 131 | 2026-06-01T17:57:34 | login_attempt | user=backup | 2 |
| 132 | 2026-06-01T17:57:34 | login_attempt | user=backup | 2 |
| 133 | 2026-06-01T17:57:35 | login_attempt | user=backup | 2 |
| 134 | 2026-06-01T17:57:35 | login_attempt | user=backup | 2 |
| 135 | 2026-06-01T17:57:35 | login_attempt | user=backup | 2 |
| 136 | 2026-06-01T17:57:35 | login_attempt | user=backup | 2 |
| 137 | 2026-06-01T17:57:36 | login_attempt | user=backup | 2 |
| 138 | 2026-06-01T17:57:36 | login_attempt | user=backup | 2 |
| 139 | 2026-06-01T17:57:36 | login_attempt | user=backup | 2 |
| 140 | 2026-06-01T17:57:36 | login_attempt | user=backup | 2 |
| 141 | 2026-06-01T17:57:37 | login_attempt | user=backup | 2 |
| 142 | 2026-06-01T17:57:37 | login_attempt | user=backup | 2 |
| 143 | 2026-06-01T17:57:37 | login_attempt | user=backup | 2 |
| 144 | 2026-06-01T17:57:37 | login_attempt | user=backup | 2 |
| 145 | 2026-06-01T17:57:38 | login_attempt | user=backup | 2 |
| 146 | 2026-06-01T17:57:38 | login_attempt | user=backup | 2 |
| 147 | 2026-06-01T17:57:38 | login_attempt | user=backup | 2 |
| 148 | 2026-06-01T17:57:38 | login_attempt | user=backup | 2 |
| 149 | 2026-06-01T17:57:39 | login_attempt | user=backup | 2 |
| 150 | 2026-06-01T17:57:39 | login_attempt | user=backup | 2 |
| 151 | 2026-06-01T17:57:39 | login_attempt | user=backup | 2 |
| 152 | 2026-06-01T17:57:39 | login_attempt | user=backup | 2 |
| 153 | 2026-06-01T17:57:40 | login_attempt | user=backup | 2 |
| 154 | 2026-06-01T17:57:40 | login_attempt | user=backup | 2 |
| 155 | 2026-06-01T17:57:40 | login_attempt | user=backup | 2 |
| 156 | 2026-06-01T17:57:40 | login_attempt | user=backup | 2 |
| 157 | 2026-06-01T17:57:41 | login_attempt | user=backup | 2 |
| 158 | 2026-06-01T17:57:41 | login_attempt | user=backup | 2 |
| 159 | 2026-06-01T17:57:41 | login_attempt | user=backup | 2 |
| 160 | 2026-06-01T17:57:41 | login_attempt | user=backup | 2 |
| 161 | 2026-06-01T17:57:42 | login_attempt | user=backup | 2 |
| 162 | 2026-06-01T17:57:42 | login_attempt | user=backup | 2 |
| 163 | 2026-06-01T17:57:42 | login_attempt | user=backup | 2 |
| 164 | 2026-06-01T17:57:42 | login_attempt | user=backup | 2 |
| 165 | 2026-06-01T17:57:43 | login_attempt | user=backup | 2 |
| 166 | 2026-06-01T17:57:43 | login_attempt | user=backup | 2 |
| 167 | 2026-06-01T17:57:43 | login_attempt | user=backup | 2 |
| 168 | 2026-06-01T17:57:43 | login_attempt | user=backup | 2 |
| 169 | 2026-06-01T17:57:44 | login_attempt | user=backup | 2 |
| 170 | 2026-06-01T17:57:44 | login_attempt | user=backup | 2 |
| 171 | 2026-06-01T17:57:44 | login_attempt | user=backup | 2 |
| 172 | 2026-06-01T17:57:44 | login_attempt | user=backup | 2 |
| 173 | 2026-06-01T17:57:45 | login_attempt | user=backup | 2 |
| 174 | 2026-06-01T17:57:45 | login_attempt | user=backup | 2 |
| 175 | 2026-06-01T17:57:45 | login_attempt | user=backup | 2 |
| 176 | 2026-06-01T17:57:45 | login_attempt | user=backup | 2 |
| 177 | 2026-06-01T17:57:46 | login_attempt | user=backup | 2 |
| 178 | 2026-06-01T17:57:46 | login_attempt | user=backup | 2 |
| 179 | 2026-06-01T17:57:46 | login_attempt | user=backup | 2 |
| 180 | 2026-06-01T17:57:46 | login_attempt | user=backup | 2 |
| 181 | 2026-06-01T17:57:47 | login_attempt | user=backup | 2 |
| 182 | 2026-06-01T17:57:47 | login_attempt | user=backup | 2 |
| 183 | 2026-06-01T17:57:47 | login_attempt | user=backup | 2 |
| 184 | 2026-06-01T17:57:47 | login_attempt | user=backup | 2 |
| 185 | 2026-06-01T17:57:48 | login_attempt | user=backup | 2 |
| 186 | 2026-06-01T17:57:48 | login_attempt | user=backup | 2 |
| 187 | 2026-06-01T17:57:48 | login_attempt | user=backup | 2 |
| 188 | 2026-06-01T17:57:48 | login_attempt | user=backup | 2 |
| 189 | 2026-06-01T17:57:49 | login_attempt | user=backup | 2 |
| 190 | 2026-06-01T17:57:49 | login_attempt | user=backup | 2 |
| 191 | 2026-06-01T17:57:49 | login_attempt | user=backup | 2 |
| 192 | 2026-06-01T17:57:49 | login_attempt | user=backup | 2 |
| 193 | 2026-06-01T17:57:50 | login_attempt | user=backup | 2 |
| 194 | 2026-06-01T17:57:50 | login_attempt | user=backup | 2 |
| 195 | 2026-06-01T17:57:50 | login_attempt | user=backup | 2 |
| 196 | 2026-06-01T17:57:50 | login_attempt | user=backup | 2 |
| 197 | 2026-06-01T17:57:51 | login_attempt | user=backup | 2 |
| 198 | 2026-06-01T17:57:51 | login_attempt | user=backup | 2 |
| 199 | 2026-06-01T17:57:51 | login_attempt | user=backup | 2 |
| 200 | 2026-06-01T17:57:51 | login_attempt | user=backup | 2 |
| 201 | 2026-06-01T17:57:52 | login_attempt | user=backup | 2 |
| 202 | 2026-06-01T17:57:52 | login_attempt | user=backup | 2 |
| 203 | 2026-06-01T17:57:52 | connection | | 1 |
| 204 | 2026-06-01T17:57:52 | connection | | 1 |
| 205 | 2026-06-01T17:57:52 | login_attempt | user=backup | 2 |
| 206 | 2026-06-01T17:57:52 | login_attempt | user=backup | 2 |
| 207 | 2026-06-01T17:57:53 | connection | | 1 |
| 208 | 2026-06-01T17:57:53 | connection | | 1 |
| 209 | 2026-06-01T17:57:53 | login_attempt | user=backup | 2 |
| 210 | 2026-06-01T17:57:53 | login_attempt | user=backup | 2 |
| 211 | 2026-06-01T17:57:53 | login_attempt | user=backup | 2 |
| 212 | 2026-06-01T17:57:53 | login_attempt | user=backup | 2 |
| 213 | 2026-06-01T17:57:54 | login_attempt | user=backup | 2 |
| 214 | 2026-06-01T17:57:54 | login_attempt | user=backup | 2 |
| 215 | 2026-06-01T17:57:54 | login_attempt | user=backup | 2 |
| 216 | 2026-06-01T17:57:54 | login_attempt | user=backup | 2 |
| 217 | 2026-06-01T17:57:55 | login_attempt | user=backup | 2 |
| 218 | 2026-06-01T17:57:55 | login_attempt | user=backup | 2 |
| 219 | 2026-06-01T17:57:55 | login_attempt | user=backup | 2 |
| 220 | 2026-06-01T17:57:55 | connection | | 1 |
| 221 | 2026-06-01T17:57:55 | login_attempt | user=ubuntu | 2 |
| 222 | 2026-06-01T17:57:56 | connection | | 1 |
| 223 | 2026-06-01T17:57:56 | connection | | 1 |
| 224 | 2026-06-01T17:57:56 | connection | | 1 |
| 225 | 2026-06-01T17:57:56 | login_attempt | user=ubuntu | 2 |
| 226 | 2026-06-01T17:57:56 | login_attempt | user=ubuntu | 2 |
| 227 | 2026-06-01T17:57:56 | login_attempt | user=ubuntu | 2 |
| 228 | 2026-06-01T17:57:56 | login_attempt | user=ubuntu | 2 |
| 229 | 2026-06-01T17:57:57 | login_attempt | user=ubuntu | 2 |
| 230 | 2026-06-01T17:57:57 | login_attempt | user=ubuntu | 2 |
| 231 | 2026-06-01T17:57:57 | login_attempt | user=ubuntu | 2 |
| 232 | 2026-06-01T17:57:57 | login_attempt | user=ubuntu | 2 |
| 233 | 2026-06-01T17:57:58 | login_attempt | user=ubuntu | 2 |
| 234 | 2026-06-01T17:57:58 | login_attempt | user=ubuntu | 2 |
| 235 | 2026-06-01T17:57:58 | login_attempt | user=ubuntu | 2 |
| 236 | 2026-06-01T17:57:58 | login_attempt | user=ubuntu | 2 |
| 237 | 2026-06-01T17:57:59 | login_attempt | user=ubuntu | 2 |
| 238 | 2026-06-01T17:57:59 | login_attempt | user=ubuntu | 2 |
| 239 | 2026-06-01T17:57:59 | login_attempt | user=ubuntu | 2 |
| 240 | 2026-06-01T17:57:59 | login_attempt | user=ubuntu | 2 |
| 241 | 2026-06-01T17:58:00 | login_attempt | user=ubuntu | 2 |
| 242 | 2026-06-01T17:58:00 | login_attempt | user=ubuntu | 2 |
| 243 | 2026-06-01T17:58:00 | login_attempt | user=ubuntu | 2 |
| 244 | 2026-06-01T17:58:00 | login_attempt | user=ubuntu | 2 |
| 245 | 2026-06-01T17:58:01 | login_attempt | user=ubuntu | 2 |
| 246 | 2026-06-01T17:58:01 | login_attempt | user=ubuntu | 2 |
| 247 | 2026-06-01T17:58:01 | login_attempt | user=ubuntu | 2 |
| 248 | 2026-06-01T17:58:01 | login_attempt | user=ubuntu | 2 |
| 249 | 2026-06-01T17:58:02 | login_attempt | user=ubuntu | 2 |
| 250 | 2026-06-01T17:58:02 | login_attempt | user=ubuntu | 2 |
| 251 | 2026-06-01T17:58:02 | login_attempt | user=ubuntu | 2 |
| 252 | 2026-06-01T17:58:02 | login_attempt | user=ubuntu | 2 |
| 253 | 2026-06-01T17:58:03 | login_attempt | user=ubuntu | 2 |
| 254 | 2026-06-01T17:58:03 | login_attempt | user=ubuntu | 2 |
| 255 | 2026-06-01T17:58:03 | login_attempt | user=ubuntu | 2 |
| 256 | 2026-06-01T17:58:03 | login_attempt | user=ubuntu | 2 |
| 257 | 2026-06-01T17:58:04 | login_attempt | user=ubuntu | 2 |
| 258 | 2026-06-01T17:58:04 | login_attempt | user=ubuntu | 2 |
| 259 | 2026-06-01T17:58:04 | login_attempt | user=ubuntu | 2 |
| 260 | 2026-06-01T17:58:04 | login_attempt | user=ubuntu | 2 |
| 261 | 2026-06-01T17:58:05 | login_attempt | user=ubuntu | 2 |
| 262 | 2026-06-01T17:58:05 | login_attempt | user=ubuntu | 2 |
| 263 | 2026-06-01T17:58:05 | login_attempt | user=ubuntu | 2 |
| 264 | 2026-06-01T17:58:05 | login_attempt | user=ubuntu | 2 |
| 265 | 2026-06-01T17:58:06 | login_attempt | user=ubuntu | 2 |
| 266 | 2026-06-01T17:58:06 | login_attempt | user=ubuntu | 2 |
| 267 | 2026-06-01T17:58:06 | login_attempt | user=ubuntu | 2 |
| 268 | 2026-06-01T17:58:06 | login_attempt | user=ubuntu | 2 |
| 269 | 2026-06-01T17:58:07 | login_attempt | user=ubuntu | 2 |
| 270 | 2026-06-01T17:58:07 | login_attempt | user=ubuntu | 2 |
| 271 | 2026-06-01T17:58:07 | login_attempt | user=ubuntu | 2 |
| 272 | 2026-06-01T17:58:07 | login_attempt | user=ubuntu | 2 |
| 273 | 2026-06-01T17:58:08 | login_attempt | user=ubuntu | 2 |
| 274 | 2026-06-01T17:58:08 | login_attempt | user=ubuntu | 2 |
| 275 | 2026-06-01T17:58:08 | login_attempt | user=ubuntu | 2 |
| 276 | 2026-06-01T17:58:08 | login_attempt | user=ubuntu | 2 |
| 277 | 2026-06-01T17:58:09 | login_attempt | user=ubuntu | 2 |
| 278 | 2026-06-01T17:58:09 | login_attempt | user=ubuntu | 2 |
| 279 | 2026-06-01T17:58:09 | login_attempt | user=ubuntu | 2 |
| 280 | 2026-06-01T17:58:09 | login_attempt | user=ubuntu | 2 |
| 281 | 2026-06-01T17:58:10 | login_attempt | user=ubuntu | 2 |
| 282 | 2026-06-01T17:58:10 | login_attempt | user=ubuntu | 2 |
| 283 | 2026-06-01T17:58:10 | login_attempt | user=ubuntu | 2 |
| 284 | 2026-06-01T17:58:10 | login_attempt | user=ubuntu | 2 |
| 285 | 2026-06-01T17:58:11 | login_attempt | user=ubuntu | 2 |
| 286 | 2026-06-01T17:58:11 | login_attempt | user=ubuntu | 2 |
| 287 | 2026-06-01T17:58:11 | login_attempt | user=ubuntu | 2 |
| 288 | 2026-06-01T17:58:11 | login_attempt | user=ubuntu | 2 |
| 289 | 2026-06-01T17:58:12 | login_attempt | user=ubuntu | 2 |
| 290 | 2026-06-01T17:58:12 | login_attempt | user=ubuntu | 2 |
| 291 | 2026-06-01T17:58:12 | login_attempt | user=ubuntu | 2 |
| 292 | 2026-06-01T17:58:12 | login_attempt | user=ubuntu | 2 |
| 293 | 2026-06-01T17:58:13 | login_attempt | user=ubuntu | 2 |
| 294 | 2026-06-01T17:58:13 | login_attempt | user=ubuntu | 2 |
| 295 | 2026-06-01T17:58:13 | login_attempt | user=ubuntu | 2 |
| 296 | 2026-06-01T17:58:13 | login_attempt | user=ubuntu | 2 |
| 297 | 2026-06-01T17:58:14 | login_attempt | user=ubuntu | 2 |
| 298 | 2026-06-01T17:58:14 | login_attempt | user=ubuntu | 2 |
| 299 | 2026-06-01T17:58:14 | login_attempt | user=ubuntu | 2 |
| 300 | 2026-06-01T17:58:14 | login_attempt | user=ubuntu | 2 |
| 301 | 2026-06-01T17:58:15 | login_attempt | user=ubuntu | 2 |
| 302 | 2026-06-01T17:58:15 | login_attempt | user=ubuntu | 2 |
| 303 | 2026-06-01T17:58:15 | login_attempt | user=ubuntu | 2 |
| 304 | 2026-06-01T17:58:15 | login_attempt | user=ubuntu | 2 |
| 305 | 2026-06-01T17:58:16 | login_attempt | user=ubuntu | 2 |
| 306 | 2026-06-01T17:58:16 | login_attempt | user=ubuntu | 2 |
| 307 | 2026-06-01T17:58:16 | connection | | 1 |
| 308 | 2026-06-01T17:58:16 | login_attempt | user=ubuntu | 2 |
| 309 | 2026-06-01T17:58:16 | login_attempt | user=ubuntu | 2 |
| 310 | 2026-06-01T17:58:17 | connection | | 1 |
| 311 | 2026-06-01T17:58:17 | connection | | 1 |
| 312 | 2026-06-01T17:58:17 | connection | | 1 |
| 313 | 2026-06-01T17:58:17 | login_attempt | user=ubuntu | 2 |
| 314 | 2026-06-01T17:58:17 | login_attempt | user=ubuntu | 2 |
| 315 | 2026-06-01T17:58:17 | login_attempt | user=ubuntu | 2 |
| 316 | 2026-06-01T17:58:17 | login_attempt | user=ubuntu | 2 |
| 317 | 2026-06-01T17:58:18 | login_attempt | user=ubuntu | 2 |
| 318 | 2026-06-01T17:58:18 | login_attempt | user=ubuntu | 2 |
| 319 | 2026-06-01T17:58:18 | login_attempt | user=ubuntu | 2 |
| 320 | 2026-06-01T17:58:18 | login_attempt | user=ubuntu | 2 |
| 321 | 2026-06-01T17:58:19 | login_attempt | user=ubuntu | 2 |
| 322 | 2026-06-01T17:58:19 | login_attempt | user=ubuntu | 2 |
| 323 | 2026-06-01T17:58:19 | login_attempt | user=ubuntu | 2 |
| 324 | 2026-06-01T17:58:19 | login_attempt | user=ubuntu | 2 |
| 325 | 2026-06-01T17:58:20 | connection | | 1 |
| 326 | 2026-06-01T17:58:20 | connection | | 1 |
| 327 | 2026-06-01T17:58:20 | connection | | 1 |
| 328 | 2026-06-01T17:58:20 | connection | | 1 |
| 329 | 2026-06-01T17:58:20 | login_attempt | user=pi | 2 |
| 330 | 2026-06-01T17:58:20 | login_attempt | user=pi | 2 |
| 331 | 2026-06-01T17:58:20 | login_attempt | user=pi | 2 |
| 332 | 2026-06-01T17:58:20 | login_attempt | user=pi | 2 |
| 333 | 2026-06-01T17:58:21 | login_attempt | user=pi | 2 |
| 334 | 2026-06-01T17:58:21 | login_attempt | user=pi | 2 |
| 335 | 2026-06-01T17:58:21 | login_attempt | user=pi | 2 |
| 336 | 2026-06-01T17:58:21 | login_attempt | user=pi | 2 |
| 337 | 2026-06-01T17:58:22 | login_attempt | user=pi | 2 |
| 338 | 2026-06-01T17:58:22 | login_attempt | user=pi | 2 |
| 339 | 2026-06-01T17:58:22 | login_attempt | user=pi | 2 |
| 340 | 2026-06-01T17:58:22 | login_attempt | user=pi | 2 |
| 341 | 2026-06-01T17:58:23 | login_attempt | user=pi | 2 |
| 342 | 2026-06-01T17:58:23 | login_attempt | user=pi | 2 |
| 343 | 2026-06-01T17:58:23 | login_attempt | user=pi | 2 |
| 344 | 2026-06-01T17:58:23 | login_attempt | user=pi | 2 |
| 345 | 2026-06-01T17:58:24 | login_attempt | user=pi | 2 |
| 346 | 2026-06-01T17:58:24 | login_attempt | user=pi | 2 |
| 347 | 2026-06-01T17:58:24 | login_attempt | user=pi | 2 |
| 348 | 2026-06-01T17:58:24 | login_attempt | user=pi | 2 |
| 349 | 2026-06-01T17:58:25 | login_attempt | user=pi | 2 |
| 350 | 2026-06-01T17:58:25 | login_attempt | user=pi | 2 |
| 351 | 2026-06-01T17:58:25 | login_attempt | user=pi | 2 |
| 352 | 2026-06-01T17:58:25 | login_attempt | user=pi | 2 |
| 353 | 2026-06-01T17:58:26 | login_attempt | user=pi | 2 |
| 354 | 2026-06-01T17:58:26 | login_attempt | user=pi | 2 |
| 355 | 2026-06-01T17:58:26 | login_attempt | user=pi | 2 |
| 356 | 2026-06-01T17:58:26 | login_attempt | user=pi | 2 |
| 357 | 2026-06-01T17:58:27 | login_attempt | user=pi | 2 |
| 358 | 2026-06-01T17:58:27 | login_attempt | user=pi | 2 |
| 359 | 2026-06-01T17:58:27 | login_attempt | user=pi | 2 |
| 360 | 2026-06-01T17:58:27 | login_attempt | user=pi | 2 |
| 361 | 2026-06-01T17:58:28 | login_attempt | user=pi | 2 |
| 362 | 2026-06-01T17:58:28 | login_attempt | user=pi | 2 |
| 363 | 2026-06-01T17:58:28 | login_attempt | user=pi | 2 |
| 364 | 2026-06-01T17:58:28 | login_attempt | user=pi | 2 |
| 365 | 2026-06-01T17:58:29 | login_attempt | user=pi | 2 |
| 366 | 2026-06-01T17:58:29 | login_attempt | user=pi | 2 |
| 367 | 2026-06-01T17:58:29 | login_attempt | user=pi | 2 |
| 368 | 2026-06-01T17:58:29 | login_attempt | user=pi | 2 |
| 369 | 2026-06-01T17:58:30 | login_attempt | user=pi | 2 |
| 370 | 2026-06-01T17:58:30 | login_attempt | user=pi | 2 |
| 371 | 2026-06-01T17:58:30 | login_attempt | user=pi | 2 |
| 372 | 2026-06-01T17:58:30 | login_attempt | user=pi | 2 |
| 373 | 2026-06-01T17:58:31 | login_attempt | user=pi | 2 |
| 374 | 2026-06-01T17:58:31 | login_attempt | user=pi | 2 |
| 375 | 2026-06-01T17:58:31 | login_attempt | user=pi | 2 |
| 376 | 2026-06-01T17:58:31 | login_attempt | user=pi | 2 |
| 377 | 2026-06-01T17:58:32 | login_attempt | user=pi | 2 |
| 378 | 2026-06-01T17:58:32 | login_attempt | user=pi | 2 |
| 379 | 2026-06-01T17:58:32 | login_attempt | user=pi | 2 |
| 380 | 2026-06-01T17:58:32 | login_attempt | user=pi | 2 |
| 381 | 2026-06-01T17:58:33 | login_attempt | user=pi | 2 |
| 382 | 2026-06-01T17:58:33 | login_attempt | user=pi | 2 |
| 383 | 2026-06-01T17:58:33 | login_attempt | user=pi | 2 |
| 384 | 2026-06-01T17:58:33 | login_attempt | user=pi | 2 |
| 385 | 2026-06-01T17:58:34 | login_attempt | user=pi | 2 |
| 386 | 2026-06-01T17:58:34 | login_attempt | user=pi | 2 |
| 387 | 2026-06-01T17:58:34 | login_attempt | user=pi | 2 |
| 388 | 2026-06-01T17:58:34 | login_attempt | user=pi | 2 |
| 389 | 2026-06-01T17:58:35 | login_attempt | user=pi | 2 |
| 390 | 2026-06-01T17:58:35 | login_attempt | user=pi | 2 |
| 391 | 2026-06-01T17:58:35 | login_attempt | user=pi | 2 |
| 392 | 2026-06-01T17:58:35 | login_attempt | user=pi | 2 |
| 393 | 2026-06-01T17:58:36 | login_attempt | user=pi | 2 |
| 394 | 2026-06-01T17:58:36 | login_attempt | user=pi | 2 |
| 395 | 2026-06-01T17:58:36 | login_attempt | user=pi | 2 |
| 396 | 2026-06-01T17:58:36 | login_attempt | user=pi | 2 |
| 397 | 2026-06-01T17:58:37 | login_attempt | user=pi | 2 |
| 398 | 2026-06-01T17:58:37 | login_attempt | user=pi | 2 |
| 399 | 2026-06-01T17:58:37 | login_attempt | user=pi | 2 |
| 400 | 2026-06-01T17:58:37 | login_attempt | user=pi | 2 |
| 401 | 2026-06-01T17:58:38 | login_attempt | user=pi | 2 |
| 402 | 2026-06-01T17:58:38 | login_attempt | user=pi | 2 |
| 403 | 2026-06-01T17:58:38 | login_attempt | user=pi | 2 |
| 404 | 2026-06-01T17:58:38 | login_attempt | user=pi | 2 |
| 405 | 2026-06-01T17:58:39 | login_attempt | user=pi | 2 |
| 406 | 2026-06-01T17:58:39 | login_attempt | user=pi | 2 |
| 407 | 2026-06-01T17:58:39 | login_attempt | user=pi | 2 |
| 408 | 2026-06-01T17:58:39 | login_attempt | user=pi | 2 |
| 409 | 2026-06-01T17:58:40 | login_attempt | user=pi | 2 |
| 410 | 2026-06-01T17:58:40 | login_attempt | user=pi | 2 |
| 411 | 2026-06-01T17:58:40 | login_attempt | user=pi | 2 |
| 412 | 2026-06-01T17:58:40 | login_attempt | user=pi | 2 |
| 413 | 2026-06-01T17:58:41 | connection | | 1 |
| 414 | 2026-06-01T17:58:41 | connection | | 1 |
| 415 | 2026-06-01T17:58:41 | connection | | 1 |
| 416 | 2026-06-01T17:58:41 | connection | | 1 |
| 417 | 2026-06-01T17:58:41 | login_attempt | user=pi | 2 |
| 418 | 2026-06-01T17:58:41 | login_attempt | user=pi | 2 |
| 419 | 2026-06-01T17:58:41 | login_attempt | user=pi | 2 |
| 420 | 2026-06-01T17:58:41 | login_attempt | user=pi | 2 |
| 421 | 2026-06-01T17:58:42 | login_attempt | user=pi | 2 |
| 422 | 2026-06-01T17:58:42 | login_attempt | user=pi | 2 |
| 423 | 2026-06-01T17:58:42 | login_attempt | user=pi | 2 |
| 424 | 2026-06-01T17:58:42 | login_attempt | user=pi | 2 |
| 425 | 2026-06-01T17:58:43 | login_attempt | user=pi | 2 |
| 426 | 2026-06-01T17:58:43 | login_attempt | user=pi | 2 |
| 427 | 2026-06-01T17:58:43 | login_attempt | user=pi | 2 |
| 428 | 2026-06-01T17:58:43 | login_attempt | user=pi | 2 |
| 429 | 2026-06-01T17:58:44 | login_attempt | user=pi | 2 |
| 430 | 2026-06-01T17:58:44 | connection | | 1 |
| 431 | 2026-06-01T17:58:44 | connection | | 1 |
| 432 | 2026-06-01T17:58:44 | connection | | 1 |
| 433 | 2026-06-01T17:58:44 | login_attempt | user=user | 2 |
| 434 | 2026-06-01T17:58:44 | login_attempt | user=user | 2 |
| 435 | 2026-06-01T17:58:44 | login_attempt | user=user | 2 |
| 436 | 2026-06-01T17:58:45 | connection | | 1 |
| 437 | 2026-06-01T17:58:45 | login_attempt | user=user | 2 |
| 438 | 2026-06-01T17:58:45 | login_attempt | user=user | 2 |
| 439 | 2026-06-01T17:58:45 | login_attempt | user=user | 2 |
| 440 | 2026-06-01T17:58:45 | login_attempt | user=user | 2 |
| 441 | 2026-06-01T17:58:46 | login_attempt | user=user | 2 |
| 442 | 2026-06-01T17:58:46 | login_attempt | user=user | 2 |
| 443 | 2026-06-01T17:58:46 | login_attempt | user=user | 2 |
| 444 | 2026-06-01T17:58:46 | login_attempt | user=user | 2 |
| 445 | 2026-06-01T17:58:47 | login_attempt | user=user | 2 |
| 446 | 2026-06-01T17:58:47 | login_attempt | user=user | 2 |
| 447 | 2026-06-01T17:58:47 | login_attempt | user=user | 2 |
| 448 | 2026-06-01T17:58:47 | login_attempt | user=user | 2 |
| 449 | 2026-06-01T17:58:48 | login_attempt | user=user | 2 |
| 450 | 2026-06-01T17:58:48 | login_attempt | user=user | 2 |
| 451 | 2026-06-01T17:58:48 | login_attempt | user=user | 2 |
| 452 | 2026-06-01T17:58:48 | login_attempt | user=user | 2 |
| 453 | 2026-06-01T17:58:49 | login_attempt | user=user | 2 |
| 454 | 2026-06-01T17:58:49 | login_attempt | user=user | 2 |
| 455 | 2026-06-01T17:58:49 | login_attempt | user=user | 2 |
| 456 | 2026-06-01T17:58:49 | login_attempt | user=user | 2 |
| 457 | 2026-06-01T17:58:50 | login_attempt | user=user | 2 |
| 458 | 2026-06-01T17:58:50 | login_attempt | user=user | 2 |
| 459 | 2026-06-01T17:58:50 | login_attempt | user=user | 2 |
| 460 | 2026-06-01T17:58:50 | login_attempt | user=user | 2 |
| 461 | 2026-06-01T17:58:51 | login_attempt | user=user | 2 |
| 462 | 2026-06-01T17:58:51 | login_attempt | user=user | 2 |
| 463 | 2026-06-01T17:58:51 | login_attempt | user=user | 2 |
| 464 | 2026-06-01T17:58:51 | login_attempt | user=user | 2 |
| 465 | 2026-06-01T17:58:52 | login_attempt | user=user | 2 |
| 466 | 2026-06-01T17:58:52 | login_attempt | user=user | 2 |
| 467 | 2026-06-01T17:58:52 | login_attempt | user=user | 2 |
| 468 | 2026-06-01T17:58:52 | login_attempt | user=user | 2 |
| 469 | 2026-06-01T17:58:53 | login_attempt | user=user | 2 |
| 470 | 2026-06-01T17:58:53 | login_attempt | user=user | 2 |
| 471 | 2026-06-01T17:58:53 | login_attempt | user=user | 2 |
| 472 | 2026-06-01T17:58:53 | login_attempt | user=user | 2 |
| 473 | 2026-06-01T17:58:54 | login_attempt | user=user | 2 |
| 474 | 2026-06-01T17:58:54 | login_attempt | user=user | 2 |
| 475 | 2026-06-01T17:58:54 | login_attempt | user=user | 2 |
| 476 | 2026-06-01T17:58:54 | login_attempt | user=user | 2 |
| 477 | 2026-06-01T17:58:55 | login_attempt | user=user | 2 |
| 478 | 2026-06-01T17:58:55 | login_attempt | user=user | 2 |
| 479 | 2026-06-01T17:58:55 | login_attempt | user=user | 2 |
| 480 | 2026-06-01T17:58:55 | login_attempt | user=user | 2 |
| 481 | 2026-06-01T17:58:56 | login_attempt | user=user | 2 |
| 482 | 2026-06-01T17:58:56 | login_attempt | user=user | 2 |
| 483 | 2026-06-01T17:58:56 | login_attempt | user=user | 2 |
| 484 | 2026-06-01T17:58:56 | login_attempt | user=user | 2 |
| 485 | 2026-06-01T17:58:57 | login_attempt | user=user | 2 |
| 486 | 2026-06-01T17:58:57 | login_attempt | user=user | 2 |
| 487 | 2026-06-01T17:58:57 | login_attempt | user=user | 2 |
| 488 | 2026-06-01T17:58:57 | login_attempt | user=user | 2 |
| 489 | 2026-06-01T17:58:58 | login_attempt | user=user | 2 |
| 490 | 2026-06-01T17:58:58 | login_attempt | user=user | 2 |
| 491 | 2026-06-01T17:58:58 | login_attempt | user=user | 2 |
| 492 | 2026-06-01T17:58:58 | login_attempt | user=user | 2 |
| 493 | 2026-06-01T17:58:59 | login_attempt | user=user | 2 |
| 494 | 2026-06-01T17:58:59 | login_attempt | user=user | 2 |
| 495 | 2026-06-01T17:58:59 | login_attempt | user=user | 2 |
| 496 | 2026-06-01T17:58:59 | login_attempt | user=user | 2 |
| 497 | 2026-06-01T17:59:00 | login_attempt | user=user | 2 |
| 498 | 2026-06-01T17:59:00 | login_attempt | user=user | 2 |
| 499 | 2026-06-01T17:59:00 | login_attempt | user=user | 2 |
| 500 | 2026-06-01T17:59:00 | login_attempt | user=user | 2 |
| 501 | 2026-06-01T17:59:01 | login_attempt | user=user | 2 |
| 502 | 2026-06-01T17:59:01 | login_attempt | user=user | 2 |
| 503 | 2026-06-01T17:59:01 | login_attempt | user=user | 2 |
| 504 | 2026-06-01T17:59:01 | login_attempt | user=user | 2 |
| 505 | 2026-06-01T17:59:02 | login_attempt | user=user | 2 |
| 506 | 2026-06-01T17:59:02 | login_attempt | user=user | 2 |
| 507 | 2026-06-01T17:59:02 | login_attempt | user=user | 2 |
| 508 | 2026-06-01T17:59:02 | login_attempt | user=user | 2 |
| 509 | 2026-06-01T17:59:03 | login_attempt | user=user | 2 |
| 510 | 2026-06-01T17:59:03 | login_attempt | user=user | 2 |
| 511 | 2026-06-01T17:59:03 | login_attempt | user=user | 2 |
| 512 | 2026-06-01T17:59:03 | login_attempt | user=user | 2 |
| 513 | 2026-06-01T17:59:04 | login_attempt | user=user | 2 |
| 514 | 2026-06-01T17:59:04 | login_attempt | user=user | 2 |
| 515 | 2026-06-01T17:59:04 | login_attempt | user=user | 2 |
| 516 | 2026-06-01T17:59:04 | login_attempt | user=user | 2 |
| 517 | 2026-06-01T17:59:05 | login_attempt | user=user | 2 |
| 518 | 2026-06-01T17:59:05 | connection | | 1 |
| 519 | 2026-06-01T17:59:05 | connection | | 1 |
| 520 | 2026-06-01T17:59:05 | connection | | 1 |
| 521 | 2026-06-01T17:59:05 | login_attempt | user=user | 2 |
| 522 | 2026-06-01T17:59:05 | login_attempt | user=user | 2 |
| 523 | 2026-06-01T17:59:05 | login_attempt | user=user | 2 |
| 524 | 2026-06-01T17:59:06 | connection | | 1 |
| 525 | 2026-06-01T17:59:06 | login_attempt | user=user | 2 |
| 526 | 2026-06-01T17:59:06 | login_attempt | user=user | 2 |
| 527 | 2026-06-01T17:59:06 | login_attempt | user=user | 2 |
| 528 | 2026-06-01T17:59:06 | login_attempt | user=user | 2 |
| 529 | 2026-06-01T17:59:07 | login_attempt | user=user | 2 |
| 530 | 2026-06-01T17:59:07 | login_attempt | user=user | 2 |
| 531 | 2026-06-01T17:59:07 | login_attempt | user=user | 2 |
| 532 | 2026-06-01T17:59:07 | login_attempt | user=user | 2 |
| 533 | 2026-06-01T17:59:08 | login_attempt | user=user | 2 |
| 534 | 2026-06-01T17:59:08 | login_attempt | user=user | 2 |
| 535 | 2026-06-01T17:59:08 | connection | | 1 |
| 536 | 2026-06-01T17:59:08 | connection | | 1 |
| 537 | 2026-06-01T17:59:08 | login_attempt | user=test | 2 |
| 538 | 2026-06-01T17:59:08 | login_attempt | user=test | 2 |
| 539 | 2026-06-01T17:59:09 | connection | | 1 |
| 540 | 2026-06-01T17:59:09 | connection | | 1 |
| 541 | 2026-06-01T17:59:09 | login_attempt | user=test | 2 |
| 542 | 2026-06-01T17:59:09 | login_attempt | user=test | 2 |
| 543 | 2026-06-01T17:59:09 | login_attempt | user=test | 2 |
| 544 | 2026-06-01T17:59:09 | login_attempt | user=test | 2 |
| 545 | 2026-06-01T17:59:10 | login_attempt | user=test | 2 |
| 546 | 2026-06-01T17:59:10 | login_attempt | user=test | 2 |
| 547 | 2026-06-01T17:59:10 | login_attempt | user=test | 2 |
| 548 | 2026-06-01T17:59:10 | login_attempt | user=test | 2 |
| 549 | 2026-06-01T17:59:11 | login_attempt | user=test | 2 |
| 550 | 2026-06-01T17:59:11 | login_attempt | user=test | 2 |
| 551 | 2026-06-01T17:59:11 | login_attempt | user=test | 2 |
| 552 | 2026-06-01T17:59:11 | login_attempt | user=test | 2 |
| 553 | 2026-06-01T17:59:12 | login_attempt | user=test | 2 |
| 554 | 2026-06-01T17:59:12 | login_attempt | user=test | 2 |
| 555 | 2026-06-01T17:59:12 | login_attempt | user=test | 2 |
| 556 | 2026-06-01T17:59:12 | login_attempt | user=test | 2 |

---

## Behavior Switches

| When | Transition | Score at Switch | Latency | Timestamp |
|---|---|---|---|---|
| — | — | — | — | — |

---

## Engagement Analysis

- **Final Score:** 1063
- **Peak Engagement:** 1063 (final)
- **Steps Monitored:** 13
- **Behavior Switches:** 0

---

## Collected Intelligence

**Usernames attempted:** root, admin, backup, ubuntu, pi, user, test



---

## Deception Assessment

### Decoys Accessed

- None recorded

---

## Recommendation

HIGH engagement detected. Attacker deeply interacted with decoys. Recommend: collect all forensic artifacts, block source IP at perimeter, escalate to threat intel team.

---

*Generated by honeypot_manager.py — OpenClaw Honeypot Orchestration System*
