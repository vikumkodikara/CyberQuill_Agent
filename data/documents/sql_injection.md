# SQL Injection Attack Vectors and Prevention

## Overview
SQL injection (SQLi) is a code injection technique that exploits vulnerabilities in an application's database layer. It occurs when user-supplied input is incorporated into SQL queries without proper validation or sanitization. SQL injection remains one of the most critical web application vulnerabilities, ranked as part of A03:2021 – Injection in the OWASP Top 10. Successful SQL injection attacks can lead to unauthorized data access, data modification, data deletion, authentication bypass, and in some cases remote code execution on the database server.

## Types of SQL Injection

### In-Band SQL Injection (Classic)
In-band SQL injection is the most common and straightforward type where the attacker uses the same communication channel to launch the attack and gather results.

#### Error-Based SQL Injection
The attacker crafts input that causes the database to generate error messages. These error messages reveal information about the database structure. For example, injecting a single quote into a login field may produce an error like "You have an error in your SQL syntax near '''" which confirms the application is vulnerable. The attacker then uses increasingly specific queries to extract table names, column names, and data from error messages.

#### Union-Based SQL Injection
The attacker uses the UNION SQL operator to combine the results of the original query with results from injected queries. This technique requires the attacker to determine the number of columns returned by the original query and find columns with compatible data types. For example, an attacker might inject: ' UNION SELECT username, password FROM users -- to retrieve credentials from the users table appended to the legitimate query results.

### Inferential SQL Injection (Blind)
In blind SQL injection, no data is directly returned to the attacker through the web application. The attacker reconstructs information by observing the application's behavior.

#### Boolean-Based Blind SQL Injection
The attacker sends queries that result in either a TRUE or FALSE condition, observing differences in the application's response. For example, injecting ' AND 1=1 -- returns a normal page while ' AND 1=2 -- returns a different response. By systematically testing conditions, the attacker can extract data one bit at a time, determining database names, table names, and data character by character.

#### Time-Based Blind SQL Injection
The attacker uses SQL commands that cause time delays to infer information. For example, injecting ' OR IF(1=1, SLEEP(5), 0) -- causes a 5-second delay if the condition is true. The attacker measures response times to determine if conditions are true or false. This technique is slower but works even when the application shows identical responses for all inputs.

### Out-of-Band SQL Injection
Out-of-band SQL injection occurs when the attacker cannot use the same channel to launch the attack and gather results. The attacker uses alternative channels such as DNS lookups or HTTP requests to exfiltrate data. For example, using xp_dirtree in MSSQL to trigger a DNS lookup to an attacker-controlled domain with the extracted data embedded in the subdomain. This technique requires the database server to have outbound network connectivity.

## Common SQL Injection Attack Vectors

### Authentication Bypass
Attackers inject SQL into login forms to bypass authentication. A classic example is entering ' OR '1'='1 as the username and any value as the password. This modifies the authentication query to always return true, granting access without valid credentials. More sophisticated attacks can target specific user accounts, for example: admin'-- which comments out the password check entirely.

### Data Exfiltration
Attackers extract sensitive data from the database. Using UNION-based injection, attackers can retrieve data from any table the database user has access to. This includes customer records, financial data, credentials, and personal information. Attackers can also access database metadata tables (information_schema in MySQL, sys.tables in MSSQL) to enumerate the entire database structure.

### Data Manipulation
SQL injection can be used to modify or delete data. Attackers can inject INSERT, UPDATE, or DELETE statements to add rogue administrator accounts, modify prices or financial records, delete audit logs to cover tracks, and alter application content or configuration stored in the database.

### Remote Code Execution
In some configurations, SQL injection can lead to operating system command execution. In MSSQL, the xp_cmdshell extended stored procedure allows command execution. In MySQL, the INTO OUTFILE command can write files to disk including web shells. In PostgreSQL, the COPY command or custom functions can execute system commands. This escalation turns a web vulnerability into full server compromise.

### Second-Order SQL Injection
Second-order SQL injection occurs when user input is stored in the database and later incorporated into SQL queries without sanitization. For example, a user registers with the username admin'-- which is safely stored. Later, when the application retrieves this username and uses it in another query without sanitization, the injection is triggered. This type is harder to detect because the injection point and execution point are different.

## SQL Injection Prevention

### Parameterized Queries (Prepared Statements)
The most effective defense against SQL injection is using parameterized queries. Instead of concatenating user input into SQL strings, use placeholders that the database driver fills in safely. In Python with psycopg2: cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,)). In Java with JDBC: PreparedStatement stmt = conn.prepareStatement("SELECT * FROM users WHERE id = ?"); stmt.setInt(1, userId). The database treats parameters as data, never as executable SQL code.

### Stored Procedures
Use stored procedures with parameterized inputs to encapsulate database logic. Stored procedures can restrict the SQL statements that the application can execute. However, stored procedures must also use parameterized queries internally, as dynamic SQL within stored procedures is still vulnerable to injection.

### Input Validation
Implement strict input validation as a defense-in-depth measure. Use whitelist validation to accept only expected characters and formats. Validate data types, length, range, and format on the server side. Reject input containing SQL metacharacters when possible. Note that input validation alone is insufficient and should always be combined with parameterized queries.

### Output Encoding
Encode output data to prevent injection in different contexts. Use context-appropriate encoding for HTML, JavaScript, URL, and SQL contexts. This prevents stored SQL injection payloads from being executed in secondary contexts.

### Least Privilege Database Access
Configure database accounts with minimal necessary permissions. Use separate database accounts for different application functions (read-only for reporting, read-write for transactions). Never connect to the database as a superuser or DBA account from web applications. Remove or disable unnecessary database features and stored procedures (like xp_cmdshell in MSSQL). Restrict database account permissions to specific tables and operations.

### Web Application Firewall (WAF)
Deploy a WAF as an additional layer of defense. WAFs can detect and block common SQL injection patterns using signature-based and anomaly-based detection. Configure WAF rules specific to the application's expected traffic patterns. Use WAF logging to identify and investigate potential attacks. Note that WAFs should not be the sole defense as they can be bypassed with obfuscation techniques.

## SQL Injection Detection

### Static Application Security Testing (SAST)
Use SAST tools to analyze source code for SQL injection vulnerabilities during development. Tools scan for string concatenation in SQL queries, missing parameterization, and unsafe use of user input. Integrate SAST into CI/CD pipelines to catch vulnerabilities before deployment.

### Dynamic Application Security Testing (DAST)
Use DAST tools to test running applications for SQL injection vulnerabilities. Tools like SQLMap, Burp Suite, and OWASP ZAP automatically test input fields with injection payloads. DAST testing simulates real attacker behavior and identifies vulnerabilities that SAST may miss.

### Runtime Application Self-Protection (RASP)
RASP technology instruments the application to detect and prevent SQL injection at runtime. It monitors SQL query construction and blocks queries that deviate from expected patterns. RASP provides protection even for legacy applications that cannot easily be modified.
