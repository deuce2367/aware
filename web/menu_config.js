/* ----------------------- 
 * $RCSfile: menu_config.js,v $
 * $Revision: 1.12 $ 
 * $Date: 2008-08-21 03:55:52 $ 
 * $Author: aps1 $ 
 * $Name: not supported by cvs2svn $ 
 * ----------------------- */

function init(doit)
{
// The menu function references takes the following parameters:
//  menu(size, orientation, x, y, offsetX, offsetY, bgOut, bgOver, fontFace, fontSize, 
//        fontStyleOut, fontStyleOver, textColorOut, textColorOver, borderSize, borderColor, margin, showChar, 
//        showOnClick, sepItems, isMainMenu, hasAnimations, animationType, hasShadow, sOffX, sOffY, shadowColor)

	//Main Menu items:
	menus[0] = new menu(18, "horizontal", 0, 82, 0, 0, "#000000", "#006600", "Candara,Tahoma,sans-serif", 11, 
		"bold", "bold", "#ffffff", "#ffffff", 0, "#000000", 0, "", false, false, true, false, 11, true, 0, 0, "black");
	menus[0].addItem("/", "", 160, "center", "HOME", 0);
	menus[0].addItem("#", "", 160, "center", "SYSTEMS", 1);
	menus[0].addItem("#", "", 160, "center", "TOOLS",  2);
	menus[0].addItem("#", "", 160, "center", "ADMIN",   3);
	menus[0].addItem("#", "", 160, "center", "HELP",    4);

//Sub Menu for Main Menu Item ("Systems"):
	menus[1] = new menu(160, "vertical", 0, 0, 0, 0, "#888888", "#006600", "Candara,Tahoma,sans-serif", 10, "bold", 
		"bold", "#ffffff", "#ffcc33", 0, "#000000", 0, "", false, false, false, false, 6, true, 0, 0, "black");
	menus[1].addItem("daemon_status.cgi",   "", 18, "left", "&nbsp;Daemon Status", 0);
	menus[1].addItem("monitor.cgi",    "", 18, "left", "&nbsp;Node Monitor", 0);
	menus[1].addItem("status.cgi",    "", 18, "left", "&nbsp;Node Status", 0);
	menus[1].addItem("process.cgi",    "", 18, "left", "&nbsp;Processes", 0);
	menus[1].addItem("profile_status.cgi",    "", 18, "left", "&nbsp;Profile Status", 0);
	menus[1].addItem("alert.cgi",    "", 18, "left", "&nbsp;Alerts", 0);

//Sub Menu for Main Menu Item ("Tools"):
	menus[2] = new menu(160, "vertical", 0, 0, 0, 0, "#888888", "#006600", "Candara,Tahoma,sans-serif", 10, "bold", 
		"bold", "#ffffff", "#ffcc33", 0, "#000000", 0, "", false, false, false, false, 6, true, 0, 0, "black");
	//menus[2].addItem("calendar.cgi", "", 18, "left", "&nbsp;Daily Reports", 0);
	menus[2].addItem("database.cgi", "", 18, "left", "&nbsp;Database", 0);
	menus[2].addItem("profiles.cgi", "", 18, "left", "&nbsp;Profile Manager", 0);

//Sub Menu for Main Menu Item ("Admin"):
	menus[3] = new menu(160, "vertical", 0, 0, 0, 0, "#888888", "#006600", "Candara,Tahoma,sans-serif", 10, "bold", 
		"bold", "#ffffff", "#ffcc33", 0, "#000000", 0, "", false, false, false, false, 6, true, 0, 0, "black");
	menus[3].addItem("daemon_tasking.cgi",   "", 18, "left", "&nbsp;Daemon Tasking", 0);
	menus[3].addItem("report.cgi",   "", 18, "left", "&nbsp;List Nodes", 0);
	//menus[3].addItem("update.cgi?action=addNode",   "", 18, "left", "&nbsp;Add Node", 0);
	menus[3].addItem("update.cgi",   "", 18, "left", "&nbsp;Edit All Nodes", 0);
	menus[3].addItem("settings.cgi", "", 18, "left", "&nbsp;Settings", 0);

//Sub Menu for Main Menu Item ("Help"):
	menus[4] = new menu(160, "vertical", 0, 0, 0, 0, "#888888", "#006600", "Candara,Tahoma,sans-serif", 10, "bold", 
		"bold", "#ffffff", "#ffcc33", 0, "#000000", 0, "", false, false, false, false, 6, true, 0, 0, "black");
	menus[4].addItem("about.cgi", "", 18, "left", "&nbsp;About", 0);
	menus[4].addItem("install_guide.cgi", "", 18, "left", "&nbsp;Install Guide", 0);
	menus[4].addItem("release_notes.cgi", "", 18, "left", "&nbsp;Release Notes", 0);
	menus[4].addItem("version.cgi", "", 18, "left", "&nbsp;Version", 0);


} //OUTER CLOSING BRACKET. EVERYTHING ADDED MUST BE ABOVE THIS LINE.
