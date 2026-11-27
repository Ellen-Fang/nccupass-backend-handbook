from pathlib import Path
import html
from diagrams import diagram_for

ROOT = Path(__file__).parent
OUT = ROOT / 'dist'
OUT.mkdir(exist_ok=True)

chapters = [{'slug': 'request',
  'title': '請求流程與服務架構',
  'subtitle': '說明 DNS、HTTPS、Nginx、後端與資料庫的分工，以及政大通 API 的轉發路徑。',
  'tags': '網域・Nginx・後端・資料庫',
  'sections': [('請求處理的各層分工',
                '<p>APP 是發出請求的客戶端。DNS 協助把網域解析到入口位址；HTTPS 連線到入口後，Nginx '
                '依網域與路徑選擇服務。後端處理業務邏輯，需要資料時再向資料庫或快取查詢，最後把結果沿途傳回 '
                'APP。</p><p>一台主機可以承載多個服務；同一個網域也可以用不同路徑分送請求。服務名稱相近，並不代表它們是同一個程序。</p>'),
               ('政大通的請求路徑',
                '<p><strong>範例：餐飲服務 的請求路徑。</strong>以下以示範 餐飲服務 路由說明請求經過的層次。</p><div '
                'class="flow"><span>APP</span><span>HTTPS／443</span><span>Nginx</span><span>meal-api:8000</span><span>資料來源</span></div><p>Nginx '
                '將 <code>api.example.com/meal/</code>轉發至 '
                '<code>meal-api:8000</code>。後端實際連到哪個資料庫，仍須由連線設定確認，不能只靠容器名稱推定。</p><div '
                'class="table-wrap"><table><thead><tr><th>API 路徑</th><th>Nginx '
                '目的地</th></tr></thead><tbody><tr><td>/meal/</td><td>meal-api:8000</td></tr><tr><td>/clubs/</td><td>club-api:8000</td></tr><tr><td>/score/</td><td>score-api:8000</td></tr><tr><td>一般根路徑請求</td><td>core-api:80</td></tr></tbody></table></div>'),
               ('請求異常的影響範圍',
                '<p>排查請求異常時，先確認受影響的功能與服務範圍，再決定檢查順序。單一服務異常時，優先查看該服務的路由、程序與依賴；多個服務同時異常時，優先檢查它們共用的入口、主機資源與網路。影響範圍用來安排調查順序，實際原因仍需由狀態與日誌確認。</p><div '
                'class="example"><p class="example-label">情境範例：僅 餐飲服務 無法使用</p><p>假設 餐飲服務 請求失敗，但核心 API 與 社團服務 '
                '仍正常，先檢查 餐飲服務 的 Nginx 路由、後端容器與資料依賴。若多個 API 同時失效，再優先調查共用 '
                'Nginx、主機與網路。此處為排查情境的示例，並非已發生的故障紀錄。</p></div><p>HTTP 狀態碼提供另一項線索：502 表示閘道或代理收到無效的上游回應；500 '
                '表示伺服器遇到無法完成請求的非預期情況。調查時應對照請求時間、Nginx 與應用程式日誌，不能只依狀態碼判定故障來源。</p>')],
  'commands': 'docker ps\ndocker logs --since 10m --tail 100 meal-api',
  'commands_note': '指令範例：以下以 餐飲服務 示範查看容器狀態與最近 10 分鐘的日誌。查詢其他服務時，請替換容器名稱。'},
 {'slug': 'containers',
  'title': '主機、容器與網路',
  'subtitle': '說明主機與容器的關係、port mapping、Docker 網路，以及 Compose 專案與服務名稱。',
  'tags': 'Docker・Compose・Port・Network',
  'sections': [('一台主機，數個隔離的執行環境',
                '<p>主機提供 CPU、記憶體、磁碟與作業系統核心。Image 是建立容器的範本；container '
                '是由它啟動的執行實例。容器有自己的程序與檔案系統視角，但仍共享主機資源。</p><p>容器隔離不等於資源無限。某個服務大量消耗記憶體或磁碟，仍可能影響同一台主機上的其他服務。</p>'),
               ('主機與容器的連接埠對應',
                '<p>Port mapping 將主機的連接埠對應到容器內的連接埠。不同容器可在各自的網路命名空間使用相同 '
                'port；同一主機位址上的綁定則需避免衝突。</p><p><strong>範例：餐飲服務 的連接埠對應。</strong>主機使用 8004 接收連線，再轉到 餐飲服務 容器內的 '
                '8000：</p><div class="flow"><span>主機 :8004</span><span>port mapping</span><span>餐飲服務 容器 '
                ':8000</span></div><p>Nginx 使用 <code>meal-api:8000</code> 作為上游，透過 Docker 網路連到容器內部 port，與主機的 '
                '8004 映射是不同入口。</p><p class="note">0.0.0.0 與 IPv6 全介面綁定描述的是監聽範圍；對外可達性仍取決於 Docker '
                '網路、防火牆與主機外部的網路限制。</p>'),
               ('Docker 網路配置範例',
                '<p>以下為多服務系統的教學配置，並非政大通正式主機的網路清單。gateway、core-api 與其他需要相互連線的服務可加入 '
                'app-network；爬蟲服務與失物服務則各自建立獨立網路，連接自己的後端、資料庫與快取。</p><p>入口網站如需連接共用入口，可加入對應網路。host '
                '模式則共用主機網路命名空間，應另外考慮連接埠衝突與隔離需求。同網路提供連線條件，業務依賴仍由應用程式設定決定。</p>'),
               ('Compose 與容器名稱',
                '<p>Compose 專案、服務與容器名稱用來辨認不同層次的資源。專案將相關服務組成一組，服務名稱對應 Compose '
                '檔的服務定義，容器名稱則識別實際執行的容器。</p><p><strong>範例：核心後端的三種名稱。</strong></p><div '
                'class="table-wrap"><table><thead><tr><th>名稱類型</th><th>核心後端例子</th><th>用途</th></tr></thead><tbody><tr><td>Compose '
                'project</td><td>app-stack</td><td>辨認一組部署資源</td></tr><tr><td>Compose '
                'service</td><td>backend</td><td>Compose 檔裡的服務識別</td></tr><tr><td>Container '
                'name</td><td>core-api</td><td>辨認實際容器</td></tr></tbody></table></div><p>使用 Compose '
                '前，要先確認設定檔與專案。只在終端機切換到看似相關的資料夾，不能保證操作的是正確服務。</p>'),
               ('容器狀態與功能狀態',
                '<p><code>Up</code> 表示容器正在執行，不代表 API 的每個功能都正常。<code>healthy</code> '
                '表示通過所設定的健康檢查，其保證範圍取決於檢查內容。<code>Exited (0)</code> 也可能是一次性工作正常完成，應先確認用途。</p><p>容器顯示 Up '
                '而功能失敗時，應先核對失敗時間、HTTP 回應與相關 log，再確認路由及後端依賴。重啟前保留證據，才能追查原因。</p>')],
  'commands': 'docker ps -a\ndocker compose ls\ndocker network ls',
  'commands_note': '下列指令列出容器、Compose 專案與 Docker 網路，便於核對服務歸屬。'},
 {'slug': 'storage',
  'title': '資料保存與資料庫操作',
  'subtitle': '說明程式、設定與資料的位置、掛載與持久化，以及新增 活動服務 社團用戶的處理流程。',
  'tags': '掛載・持久化・MongoDB・用戶資料',
  'sections': [('程式、設定與資料的生命週期',
                '<p><strong>程式</strong>通常可由版本庫與建置流程重新產生；<strong>設定</strong>決定服務如何運作與連線；<strong>資料</strong>包含資料庫內容和使用者上傳檔案，通常不能靠重新部署找回。憑證也需要獨立管理，不能放進教學範例或公開版本庫。</p><p>容器的可寫層會隨容器刪除而消失。掛載把特定路徑接到主機目錄或 '
                'Docker volume，讓資料的生命週期可以獨立於容器；是否真的保存到該位置，仍取決於應用程式設定。</p>'),
               ('Bind mount 與 Docker volume',
                '<p>Bind mount 將指定的主機路徑掛入容器；volume 的儲存位置與生命週期則由 Docker '
                '管理。應用程式必須將資料寫入正確的掛載路徑，才能在容器重建後接續使用。</p><p><strong>範例：政大通服務的掛載方式。</strong>下表列出既有服務的掛載對應。</p><div '
                'class="table-wrap"><table><thead><tr><th>方式</th><th>示範服務配置</th><th>作用</th></tr></thead><tbody><tr><td>Bind '
                'mount</td><td>mongo-data → /data/db</td><td>容器路徑對應到指定主機目錄</td></tr><tr><td>Docker '
                'volume</td><td>失物服務 MySQL 的 volume → /var/lib/mysql</td><td>由 Docker '
                '管理儲存位置</td></tr><tr><td>設定檔掛載</td><td>nginx/nginx.conf → '
                '/etc/nginx/nginx.conf</td><td>服務在容器內讀取主機提供的設定</td></tr></tbody></table></div><p>失物服務 MySQL '
                '同時有掛到 <code>/data/db</code> 的主機目錄，以及掛到 <code>/var/lib/mysql</code> 的 volume。要先確認 MySQL 的實際 '
                'datadir，不能依主機資料夾名稱決定備份範圍。</p>'),
               ('共享目錄的影響範圍',
                '<p>多個容器掛入同一主機目錄時，會讀取同一份來源資料；在具有寫入權限的掛載內修改檔案，也會影響主機與其他使用該目錄的服務。</p><p><strong>範例：核心後端、檔案服務與 '
                '社團服務 的共享目錄。</strong></p><p>核心後端與檔案服務都掛入主機的 <code>file-service</code> 目錄，社團服務 後端則掛入其中的 '
                '<code>clubs</code> '
                '子目錄。它們會接觸同一棵資料目錄；操作前需確認讀寫權限與使用方式。</p><p>在容器內刪除掛載檔案時，影響不限於該容器。若該檔案位於掛載路徑，變動可能直接作用在主機資料與其他服務看到的內容。</p>'),
               ('持久化與備份的差別',
                '<p>掛載能讓資料跨容器重建保留，不能防止誤刪、損毀或主機故障。備份需要另外確認範圍、頻率、保存期限與還原方式；資料庫執行中直接複製資料目錄，不應直接視為一致且可還原的備份。</p><p>重建資料庫容器前，需確認實際資料目錄已掛載、重建會接回同一份資料，且操作不包含移除所需 '
                'volume。</p>'),
               ('新增 活動服務 社團用戶',
                '<p>新增社團用戶需要 email 與 UID。Email 由申請表單提供，UID 則從核心資料庫查詢。UID '
                '是核心帳號識別碼，不能自行產生或用學號代替。</p><ol><li><strong>確認申請資料：</strong>核對表單提供的學校信箱與社團資料。</li><li><strong>查詢核心帳號：</strong>進入核心 '
                'MongoDB 容器，選擇 ExampleApp 資料庫，以信箱查詢 UserAccounts 中的 userid。</li><li><strong>建立 活動服務 '
                '用戶：</strong>將核對後的 email、UID 與必要申請資料，依 活動服務 '
                '示範欄位格式新增至其資料庫。</li><li><strong>驗證結果：</strong>重新查詢新增紀錄，確認 email 與 UID '
                '對應正確，且沒有重複建立帳號。</li></ol><p>進入 MongoDB 時使用團隊提供的帳號，密碼於提示時輸入。下列登入指令使用主機既有的 mongo '
                'shell；帳號請依實際授權調整：</p><div class="code-wrap"><button class="copy" '
                'type="button">複製指令</button><pre><code>docker exec -it core-mongo mongo -u admin '
                '--authenticationDatabase admin '
                '-p</code></pre></div><p><strong>查詢範例：</strong>以下信箱為佔位文字，執行前請替換成表單提供的申請信箱。</p><div '
                'class="code-wrap"><button class="copy" type="button">複製指令</button><pre><code>show dbs\n'
                'use ExampleApp\n'
                'db.UserAccounts.findOne({ email: &quot;目標信箱@example.edu&quot; }, { _id: 0, userid: 1 '
                '})</code></pre></div><p>查得的 userid 即為 UID。若結果為 null 或沒有 '
                'userid，先確認信箱及帳號狀態，暫停新增，不填入猜測值。</p><p>寫入前確認 活動服務 的目標資料庫、資料表與示範欄位，檢查 email 或 UID '
                '是否已存在。操作限於此次申請資料，保留新增紀錄的識別資訊以便更正。離開 MongoDB shell 可輸入 <code>exit</code>。</p>')],
  'commands': "docker inspect --format '{{range .Mounts}}{{println .Type .Source .Destination}}{{end}}' "
              'core-mongo\n'
              'docker volume ls',
  'commands_note': '指令範例：以下以核心 MongoDB 容器示範查詢掛載；查詢其他服務時，請替換容器名稱。此處不會讀寫資料庫內容。'},
 {'slug': 'deployment',
  'title': '部署流程與版本管理',
  'subtitle': '說明程式碼、image 與運行中容器的關係，以及部署驗證、設定來源與版本回復。',
  'tags': 'CI/CD・Image・版本・驗證',
  'sections': [('CI/CD 的流程',
                '<p>CI（持續整合）負責測試與打包程式碼，CD（持續交付／部署）負責將產物發布到執行環境。部署流程串接程式碼版本、image、容器與上線驗證，讓每次更新有可追蹤的來源。</p><div '
                'class="flow"><span>提交程式碼</span><span>CI 測試與打包</span><span>手動執行 '
                'CD</span><span>主機上驗證</span></div>'),
               ('部署設定步驟',
                '<ol><li><strong>確認 port：</strong>先查看主機已使用的連接埠，避免新服務的主機 port '
                '與既有服務衝突。</li><li><strong>準備設定檔：</strong>配置 '
                '<code>docker-compose.yml</code>、<code>Dockerfile</code> 與 '
                '<code>.gitlab-ci.yml</code>，可參考既有專案，並依新服務的執行需求調整。Dockerfile 定義 image 的建置方式，Compose '
                '定義服務、網路與掛載，GitLab CI 設定則定義執行流程。</li><li><strong>設定變數：</strong>在 GitLab 的 Settings → CI/CD → '
                'Variables 設定部署需要的變數，供 pipeline 在部署時使用。</li><li><strong>選擇 Runner：</strong>在 Settings → '
                'CI/CD → Runners 選用團隊示範的 Runner，由它執行 pipeline 工作。</li><li><strong>提交與發布：</strong>將程式碼推送至 '
                '<code>main</code> 分支觸發 CI，再手動執行 CD 工作。首次部署後，到主機確認服務與功能。</li></ol>'),
               ('設定來源與運行狀態',
                '<p>版本庫保存部署設定，Runner 取得工作副本後執行建置與部署，最後由主機上的容器運行服務。Compose '
                '標籤可用來查詢容器建立時使用的設定檔與工作目錄。</p><p><strong>路徑範例：</strong>設定可能位於 Runner 工作目錄或 '
                '<code>/srv/example/app-stack</code>。這些是教學路徑，操作時需確認實際檔案與目標服務。直接修改 Runner '
                '工作副本可能在下一次部署被取代，需保留的變更應同步回部署來源。</p>'),
               ('Nginx 反向代理設定',
                '<p>新服務部署後，需要讓 Nginx 將外部網址或路徑轉發到對應服務。設定由主機檔案透過 bind mount '
                '提供給容器，修改應針對掛載來源。</p><ol><li><strong>定位設定：</strong>查看容器掛載。主設定檔為 '
                '<code>/srv/example/nginx/nginx.conf</code>，額外設定目錄為 '
                '<code>/srv/example/nginx/conf</code>。</li><li><strong>保留舊設定並新增路由：</strong>在適當的 server 區塊配置 '
                'location 與 proxy_pass，核對網域、上游名稱、網路及 port。</li><li><strong>檢查語法：</strong>執行 nginx '
                '-t，失敗時修正後重新檢查，不繼續重啟。</li><li><strong>套用設定：</strong>檢查通過後重啟 Nginx '
                '容器。此入口承接多個服務，需協調執行時機。</li><li><strong>驗證：</strong>查看容器狀態，測試新路由及既有服務。異常時查看 '
                'log，必要時恢復舊設定並重新檢查、套用。</li></ol><p><strong>設定範例：餐飲服務 路由。</strong>下列為示範路由的寫法，示範 location 與 '
                'proxy_pass 的對應。新增服務時應替換為該服務的路徑、上游名稱與 port。proxy_pass 的路徑及結尾斜線會影響轉發 URI，需與後端預期路徑一致。</p><div '
                'class="code-wrap"><button class="copy" type="button">複製指令</button><pre><code>location ^~ '
                '/meal/ {\n'
                '    proxy_pass http://meal-api:8000/;\n'
                '}</code></pre></div><p>定位掛載與檢查語法：</p><div class="code-wrap"><button class="copy" '
                'type="button">複製指令</button><pre><code>docker inspect --format &#x27;{{range '
                '.Mounts}}{{println .Source .Destination}}{{end}}&#x27; gateway\n'
                'docker exec gateway nginx -t</code></pre></div><p>以下重啟操作會套用修改並短暫影響服務，僅於語法檢查通過後執行：</p><div '
                'class="code-wrap"><button class="copy" type="button">複製指令</button><pre><code>docker restart '
                'gateway\n'
                'docker ps --filter name=gateway\n'
                'docker logs --since 5m --tail 100 '
                'gateway</code></pre></div><p>容器狀態只確認程序運行；實際網址測試才用來驗證路由與功能，兩者都需要完成。</p>'),
               ('部署驗證與版本回復',
                '<p>容器顯示 Up，只能確認程序仍在執行。部署後還需查看啟動 log、確認版本，並從實際入口測試代表性功能。</p><p>回復上一個 image '
                '只處理程式版本；環境變數、資料庫結構與資料也必須相容。部署前保留所需的舊版本與設定，並確認資料變更的復原方式。</p>')],
  'commands': 'docker compose ls\ndocker ps --format "table {{.Names}}\t{{.Image}}\t{{.Status}}"',
  'commands_note': '下列指令用於查詢狀態與設定。請確認目標環境與容器名稱，並在分享輸出前遮蔽敏感資訊。'},
 {'slug': 'diagnosis',
  'title': '故障排查與資源判讀',
  'subtitle': '整理故障範圍的判斷方式、log 的使用，以及磁碟、記憶體與 Swap 的判讀原則。',
  'tags': '症狀・Log・資源・假設',
  'sections': [('記錄症狀與影響範圍',
                '<p>記錄發生時間與時區、失敗功能、影響對象、HTTP '
                '狀態、是否每次都發生，以及最近是否部署或調整設定。釐清是單一使用者、單一功能、單一服務，還是整個入口都失效。</p><p>重現時避免在 log 或對話貼出 '
                'token、完整個資或憑證。提供足以判讀的片段與時間範圍即可。</p>'),
               ('辨認服務管理方式',
                '<p>主機同時使用 Docker 與 systemd 管理服務。先辨認管理方式，再查詢對應狀態與 log；只查看 <code>docker ps</code> '
                '會漏掉直接由主機執行的服務。</p><div class="table-wrap"><table><thead><tr><th>systemd '
                '服務</th><th>用途</th></tr></thead><tbody><tr><td>transit-api.service</td><td>公車 '
                'API（Flask）</td></tr><tr><td>gitlab-runner.service</td><td>執行 GitLab CI/CD '
                '工作</td></tr><tr><td>node_exporter.service</td><td>提供主機資源監控指標</td></tr><tr><td>grafana-agent-flow.service</td><td>觀測資料收集</td></tr><tr><td>cron.service</td><td>執行 '
                'cron 排程</td></tr></tbody></table></div><p>systemd 服務可用 <code>systemctl status</code> 查看狀態，用 '
                '<code>journalctl -u</code> 查閱服務日誌。</p>'),
               ('主機狀態與防火牆觀察',
                '<p><strong>主機範例：</strong>服務可部署於 <code>192.0.2.10</code> 的 Docker 容器中。此 IP '
                '為文件示例位址。先看容器狀態，再觀察主機資源與網路政策。</p><div '
                'class="table-wrap"><table><thead><tr><th>指令</th><th>用途與判讀重點</th></tr></thead><tbody><tr><td>docker '
                'ps</td><td>查看運行中的容器、狀態與 port mapping；-a 可包含已退出容器。</td></tr><tr><td>df '
                '-h</td><td>查看檔案系統容量、使用量與掛載位置。</td></tr><tr><td>htop</td><td>互動查看 '
                'CPU、記憶體與程序用量，辨認資源消耗來源。</td></tr><tr><td>sudo ufw status verbose</td><td>查看 UFW '
                '狀態與防火牆規則。</td></tr></tbody></table></div><p>htop 可用 q 或 F10 離開；它也能管理程序，單純觀察時不要送出終止訊號。UFW '
                '查詢僅顯示該工具管理的規則，不能單獨證明容器 port 對外可達或已受阻擋。</p>'),
               ('依假設選擇檢查項目',
                '<div '
                'class="table-wrap"><table><thead><tr><th>要驗證的假設</th><th>觀察方向</th><th>不能直接推論</th></tr></thead><tbody><tr><td>服務程序停止</td><td>容器狀態、退出原因</td><td>Up '
                '不代表功能正常</td></tr><tr><td>代理無法連上後端</td><td>Nginx 錯誤、上游與網路</td><td>502 '
                '不代表一定要重啟</td></tr><tr><td>資料依賴失敗</td><td>後端錯誤、資料庫連線</td><td>資料庫容器存在不代表連線可用</td></tr><tr><td>資源壓力</td><td>磁碟、available '
                '記憶體、持續趨勢</td><td>單次數值不能代表長期狀態</td></tr></tbody></table></div>'),
               ('資源用量的判讀原則',
                '<p>磁碟用量應搭配剩餘空間、成長速度與資料用途判斷。清理前先定位來源，區分 log、映像檔、備份與正式資料；Docker volume '
                '可能保存資料庫，不應作為一般暫存檔清除。</p><p>Linux 會使用記憶體做快取，判讀記憶體時應同時看 available 與程序用量，不能只看 free。Swap '
                '使用量表示有頁面被換出；是否正在發生記憶體壓力，還需搭配持續換入換出、用量趨勢及服務症狀。</p>'),
               ('保留診斷證據與操作紀錄',
                '<p>重啟或修改設定前，先保留相關時間、服務狀態與日誌。每次改動應有明確的目的、預期結果與復原方式；逐項調整並驗證，可避免多項變動混在一起而難以追查原因。</p><p>交接紀錄應包含發生時間、受影響功能與使用者、檢查結果、已排除的原因、已執行的改動，以及仍需補充的證據。</p>'),
               ('硬體與主機異常的聯絡', '<p>若懷疑是硬體或底層主機問題，聯絡團隊指定的主機管理窗口。提供發生時間、影響服務、錯誤與資源狀態，以及已做的檢查和改動，便於協助判斷。</p>')],
  'commands': 'df -h\n'
              'free -h\n'
              'docker stats --no-stream\n'
              'docker logs --since 10m --tail 100 meal-api\n'
              'systemctl status transit-api.service --no-pager\n'
              'journalctl -u transit-api.service --since today --no-pager -n 100\n'
              'htop\n'
              'sudo ufw status verbose',
  'commands_note': '指令範例：餐飲服務 示範 Docker 日誌查詢，公車 API 示範 systemd 狀態與日誌查詢；操作時請替換為目標服務。其餘指令用於主機資源與防火牆觀察。'},
 {'slug': 'changes',
  'title': '日常維護與備份復原',
  'subtitle': '說明設定變更、套件與安全性更新，以及資料備份、驗證與復原的日常維護流程。',
  'tags': '設定變更・套件更新・備份・復原',
  'sections': [('變更前的確認項目',
                '<ol><li><strong>目的：</strong>記錄要解決的問題與預期行為。</li><li><strong>範圍：</strong>列出受影響的環境、服務、資料與使用者。</li><li><strong>驗證：</strong>訂定成功標準、檢查項目與觀察時間。</li><li><strong>復原：</strong>保留必要的舊設定、版本與備份，確認恢復程序。</li></ol><p>唯讀查詢、設定變更、服務重啟與資料寫入的影響不同。操作前先辨認類型，再確認測試環境、協調對象與執行時機。</p>'),
               ('共用服務的變更範圍',
                '<p>共用服務的設定變更可能同時影響多個應用程式。修改前應確認依賴關係，保留原設定，並安排變更後的檢查範圍。</p><p><strong>範例：共用 Nginx '
                '的路由變更。</strong>Nginx 承接多個服務的請求，路由語法錯誤可能使整份設定無法載入。套用前需檢查語法，套用後除了新增路由，也應測試既有服務。操作流程見<a '
                'href="deployment.html#section-3">第四章：Nginx 反向代理設定</a>。</p>'),
               ('套件與安全性更新',
                '<p>apt update 更新可用套件索引，不直接升級已安裝套件；apt upgrade '
                '才會安裝可升級版本。升級過程可能要求確認或重新啟動部分服務。</p><p>先確認主機與服務狀態、必要備份與復原方式，選擇維護時間後依序執行：</p><div '
                'class="code-wrap"><button class="copy" type="button">複製指令</button><pre><code>sudo apt '
                'update\n'
                'sudo apt upgrade</code></pre></div><p>有需要時，清理不再使用的相依套件：</p><div class="code-wrap"><button '
                'class="copy" type="button">複製指令</button><pre><code>sudo apt '
                'autoremove</code></pre></div><p>先閱讀預計移除清單，確認沒有需要保留的套件，再回應確認提示。更新後檢查服務狀態與代表性功能；若系統要求重新開機，安排維護時間處理。</p>'),
               ('資料庫備份與還原',
                '<p><strong>備份配置範例：</strong>以 <code>/srv/example/backup/app_databases</code> 為備份目錄，由腳本搭配排程產生 '
                'SQL 壓縮檔。若主機時區為 UTC，臺灣時間需加 8 小時。</p><p>備份驗證應區分排程存在、檔案產生、壓縮完整性檢查與還原驗證。gzip '
                '檢查通過只代表壓縮結構完整，不能證明資料庫內容完整可用。</p><p>還原測試應在隔離環境執行，確認資料可讀、應用程式可使用與復原時間。上傳檔案及必要設定也應納入備份範圍，並規劃主機故障時仍能取回的副本。</p>'),
               ('操作紀錄與交接',
                '<p>記錄執行時間、目標環境、修改內容、驗證結果與復原方式。發生異常時，一併保留相關錯誤與已採取的處理，讓其他成員能接續判斷。</p><p>執行任何指令前，先確認目標路徑、作用環境、資料影響及回復方式。不確定操作效果時，先查明再執行。密碼、私鑰、完整環境變數與使用者資料應依團隊規範保存，不放入手冊或一般交接訊息。</p>')],
  'commands': 'docker exec gateway nginx -t\ndocker ps --filter name=gateway',
  'commands_note': '指令範例：以下以共用 Nginx 示範設定語法與容器狀態檢查。套件更新與服務重啟請依各節流程執行。'}]

def esc(s): return html.escape(s)

def shell(title, body, active=-1, toc=''):
    nav = ''.join(f'<a class="chapter-link {"active" if i == active else ""}" href="{c["slug"]}.html" ' + ('aria-current="page"' if i == active else '') + f'><span class="chapter-index">{i+1:02}</span><span>{c["title"]}</span></a>' for i,c in enumerate(chapters))
    return f'''<!doctype html><html lang="zh-Hant"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="description" content="政大通後端組主機手冊：服務架構、容器網路、資料保存、部署、故障排查與備份復原。"><title>{esc(title)}｜政大通後端組</title><link rel="stylesheet" href="style.css"><script src="app.js" defer></script></head><body><a class="skip" href="#main">跳到正文</a><header><a class="brand" href="index.html"><span class="brand-mark">N</span><span>政大通 <b>後端組</b></span></a><span class="header-label">主機手冊</span><button id="menu" aria-expanded="false" aria-controls="sidebar">章節目錄</button></header><div class="layout"><aside id="sidebar"><a class="overview {"active" if active==-1 else ""}" href="index.html">章節目錄</a><p class="nav-label">章節</p><nav aria-label="章節">{nav}</nav></aside><main id="main">{body}<footer>政大通後端組 · 主機手冊</footer></main><aside class="on-this-page">{toc}</aside></div></body></html>'''

entries = ''.join(f'<a class="contents-entry tone-{i+1}" href="{c["slug"]}.html"><span class="contents-number">{i+1:02}</span><div><h2>{c["title"]}</h2><p>{c["subtitle"]}</p><span class="card-tags">{c["tags"]}</span></div><span class="contents-read">閱讀章節</span></a>' for i,c in enumerate(chapters))
home = f'<div class="breadcrumb">章節目錄</div><section class="contents-heading"><h1>後端組主機手冊</h1><p>政大通主機的服務架構、部署與日常維護說明。選擇章節進入閱讀。本公開版的 IP、網域、路徑、服務名稱與網路配置均為教學範例。</p></section><nav class="contents-list" aria-label="手冊章節目錄">{entries}</nav>'
(OUT / 'index.html').write_text(shell('後端組主機手冊', home), encoding='utf-8')
for i, c in enumerate(chapters):
    sections = ''.join(f'<section id="section-{j}"><h2>{title}</h2>{content}{diagram_for(c["slug"], j)}</section>' for j,(title,content) in enumerate(c['sections']))
    toc = '<p class="nav-label">本章內容</p>' + ''.join(f'<a href="#section-{j}">{title}</a>' for j,(title,_) in enumerate(c['sections'])) + '<a href="#reference">指令速查</a>'
    prev = f'<a href="{chapters[i-1]["slug"]}.html"><small>上一章</small>{chapters[i-1]["title"]}</a>' if i else '<a href="index.html"><small>回到目錄</small>章節目錄</a>'
    nxt = f'<a href="{chapters[i+1]["slug"]}.html"><small>下一章</small>{chapters[i+1]["title"]}</a>' if i < 5 else '<a href="index.html"><small>回到目錄</small>章節目錄</a>'
    body = f'''<div class="breadcrumb"><a href="index.html">章節目錄</a><span>/</span>第 {i+1} 章</div><article><div class="article-head"><p class="eyebrow">第 {i+1} 章</p><h1>{c['title']}</h1><p class="lead">{c['subtitle']}</p><p class="tags">{c['tags']}</p></div>{sections}<section id="reference"><h2>指令速查</h2><p>{c['commands_note']}</p><div class="code-wrap"><button class="copy" type="button">複製指令</button><pre><code>{esc(c['commands'])}</code></pre></div></section><nav class="pagination" aria-label="章節翻頁">{prev}{nxt}</nav></article>'''
    (OUT / f'{c["slug"]}.html').write_text(shell(c['title'], body, i, toc), encoding='utf-8')
print('Generated contents + 6 chapters.')
