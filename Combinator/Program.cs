string yaraDir = "yara";
string finalRule = "yara_rules.yar";
string[] yaraRules = Directory.GetFiles(yaraDir, "*.yar");
foreach (var file in yaraRules)
{
    Console.WriteLine(file);
    var _rule = File.ReadAllText(file);
    File.AppendAllText(finalRule, $"// YARA Rule: {file.Replace("yara\\", "")} {Environment.NewLine} {_rule} {Environment.NewLine}");
}
Console.WriteLine("Complete combinng yara rules");