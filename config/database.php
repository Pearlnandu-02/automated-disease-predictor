<?php
// config/database.php - Robust Database Connection for Local XAMPP & Production Environments

$db_host = getenv('DB_HOST') ?: '127.0.0.1';
$db_port = getenv('DB_PORT') ?: '3306';
$db_name = getenv('DB_NAME') ?: 'ai_healthcare';
$db_user = getenv('DB_USER') ?: 'root';
$db_pass = getenv('DB_PASS') !== false ? getenv('DB_PASS') : '';

if (!defined('DB_HOST')) define('DB_HOST', $db_host);
if (!defined('DB_PORT')) define('DB_PORT', $db_port);
if (!defined('DB_NAME')) define('DB_NAME', $db_name);
if (!defined('DB_USER')) define('DB_USER', $db_user);
if (!defined('DB_PASS')) define('DB_PASS', $db_pass);

class Database {
    private static $instance = null;
    private $pdo = null;

    private function __construct() {
        try {
            $dsn = "mysql:host=" . DB_HOST . ";port=" . DB_PORT . ";dbname=" . DB_NAME . ";charset=utf8mb4";
            $options = [
                PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
                PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,
                PDO::ATTR_EMULATE_PREPARES => false,
            ];
            $this->pdo = new PDO($dsn, DB_USER, DB_PASS, $options);
        } catch (PDOException $e) {
            error_log("Database connection failure: " . $e->getMessage());
            $this->pdo = null;
        }
    }

    public static function getInstance() {
        if (self::$instance === null) {
            self::$instance = new Database();
        }
        return self::$instance->pdo;
    }
}

// Global helper function for seamless access across all modules
if (!function_exists('get_db_connection')) {
    function get_db_connection() {
        return Database::getInstance();
    }
}
?>
