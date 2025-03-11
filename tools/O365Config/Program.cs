using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace O365Config
{
    internal class Program
    {
        // NAME,CLIENT_ID,TENANT_ID,VALUE
        // string0,string1,string2,string3
        static string format = "<api_auth>\n//NAME\n<tenant_id>TID</tenant_id>\n<client_id>CID</client_id>\n<client_secret>SECRET</client_secret>\n<api_type>commercial</api_type>\n</api_auth>\n\n";
        static string endConf = "";
        static void Main(string[] args)
        {
            string[] _clients = File.ReadAllLines("sla.csv");
            foreach (string _client in _clients)
            {
                if (_client != "") 
                { 
                    string[] _confs = _client.Split(',');
                    Console.WriteLine(_confs[0]);
                    Console.WriteLine(_confs[1]);
                    Console.WriteLine(_confs[2]);
                    Console.WriteLine(_confs[3]);
                    endConf += format.Replace("NAME", _confs[0]).Replace("TID", _confs[2]).Replace("CID", _confs[1]).Replace("SECRET", _confs[3]);
                }
            }
            File.WriteAllText("final.conf", endConf);
            Console.WriteLine("Config written successfully!");
            Console.ReadLine();
        }
    }
}
