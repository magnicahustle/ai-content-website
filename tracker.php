<?php
// Function to parse Markdown to HTML
function parseMarkdown($markdown) {
    // Convert headers
    $markdown = preg_replace('/^# (.*)$/m', '<h1>$1</h1>', $markdown);
    $markdown = preg_replace('/^## (.*)$/m', '<h2>$1</h2>', $markdown);
    $markdown = preg_replace('/^### (.*)$/m', '<h3>$1</h3>', $markdown);

    // Convert bold text
    $markdown = preg_replace('/\*\*(.*)\*\*/', '<strong>$1</strong>', $markdown);

    // Convert paragraphs
    $markdown = '<p>' . str_replace("\n\n", '</p><p>', $markdown) . '</p>';
    $markdown = str_replace("\n", '<br>', $markdown);
    
    // Convert table
    $markdown = str_replace('|', '</td><td>', $markdown);
    $markdown = preg_replace('/<\/td><td>---<\/td><td>/m', '</td></tr><tr><td>', $markdown);
    $markdown = preg_replace('/<tr><td>/m', '</thead><tbody><tr>', $markdown, 1);
    $markdown = preg_replace('/<table>/m', '<thead>', $markdown, 1);
    $markdown = '<table>' . $markdown . '</tbody></table>';
    $markdown = preg_replace('/<\/td><td>\s*<\/td>/', '</td>', $markdown);


    return $markdown;
}

$trackerFile = 'tracker/project_tracker.md';
$content = file_exists($trackerFile) ? file_get_contents($trackerFile) : '# Project Tracker File Not Found';
$htmlContent = parseMarkdown($content);
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Project Tracker</title>
    <style>
        body { font-family: sans-serif; line-height: 1.6; color: #333; max-width: 800px; margin: 0 auto; padding: 20px; background-color: #f4f4f4; }
        h1, h2, h3 { color: #333; }
        table { border-collapse: collapse; width: 100%; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #e9e9e9; }
        tr:nth-child(even) { background-color: #f9f9f9; }
    </style>
</head>
<body>
    <?php echo $htmlContent; ?>
</body>
</html>
