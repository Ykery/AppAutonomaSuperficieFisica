#include <QApplication> 
#include <QVBoxLayout> 
#include <QToolBox>
#include <QToolButton> 
#include <QPushButton>
#include <QButtonGroup> 
#include <QFrame> 
#include <QTextStream> 
#include <QInputDialog> 

#include "teasmenu1.h" 
#include "start.xpm" 

QPushButton *option1; 
QPushButton *option2; 
QPushButton *option3; 
QPushButton *option4; 
QPushButton *option5; 

teasMenu::teasMenu(QWidget *parent)
     : QWidget(parent)
     {	
     QGridLayout *grid = new QGridLayout;
     grid->addWidget(createGroupBox(), 0, 0, 2, 2); 
     setLayout(grid);

     setWindowTitle(tr("Main TEAS menu")); 
     resize(480, 320);
     }

QGroupBox *teasMenu::createGroupBox()
     {
     QGroupBox *groupBox = new QGroupBox("Choose experiment type:");
     groupBox->setFont(QFont("Helvetica", 12)); 

     QButtonGroup *btgr = new QButtonGroup (this); 
     btgr->setExclusive(true); 

     option1 = new QPushButton( this ); 
     option1->setText("&Process Monitoring"); 
     option1->setFont(QFont("Helvetica", 13)); 
     option1->setMinimumSize(120, 35); 
     option1->setIcon(QIcon(start_xpm));
     option1->setCheckable(true);
     option1->setAutoExclusive(true); 
     option1->setFocusPolicy(Qt::NoFocus); 
     // procMonitor = new configMonitor; 
	connect(option1, SIGNAL(clicked()), this, SLOT(chooseOption1())); 

     btgr->addButton(option1);

     option2 = new QPushButton( this );
     option2->setText("&TEAS Timescan"); 
     option2->setFont(QFont("Helvetica", 13)); 
     option2->setMinimumSize(120, 35);      
     option2->setIcon(QIcon(start_xpm));
     option2->setCheckable(true);
     option2->setAutoExclusive(true); 
     option2->setFocusPolicy(Qt::NoFocus);  
     connect(option2, SIGNAL(clicked()), this, SLOT(chooseOption2())); 
     btgr->addButton(option2);

     option3 = new QPushButton( this );
     option3->setText("&MOKE Loop"); 
     option3->setFont(QFont("Helvetica", 13)); 
     option3->setMinimumSize(120, 35);      
     option3->setIcon(QIcon(start_xpm));
     option3->setCheckable(true);
     option3->setAutoExclusive(true); 
     option3->setFocusPolicy(Qt::NoFocus);  
     connect(option3, SIGNAL(clicked()), this, SLOT(chooseOption3())); 
     btgr->addButton(option3);

     option4 = new QPushButton( this ); 
     option4->setText("&Beam Profile");
     option4->setFont(QFont("Helvetica", 13)); 
     option4->setMinimumSize(120, 35); 
     option4->setIcon(QIcon(start_xpm));
     option4->setCheckable(true);
     option4->setAutoExclusive(true); 
     option4->setFocusPolicy(Qt::NoFocus); 
	connect(option4, SIGNAL(clicked()), this, SLOT(chooseOption4())); 
     btgr->addButton(option4); 

     option5 = new QPushButton( this ); 
     option5->setText("T&emperature Scan");
     option5->setFont(QFont("Helvetica", 13)); 
     option5->setMinimumSize(120, 35); 
     option5->setIcon(QIcon(start_xpm));
     option5->setCheckable(true);
     option5->setAutoExclusive(true); 
     option5->setFocusPolicy(Qt::NoFocus); 
	connect(option5, SIGNAL(clicked()), this, SLOT(chooseOption5())); 
     btgr->addButton(option5); 

     QPushButton *quit = new QPushButton("&Quit", this); 
     quit->setFont(QFont("Helvetica", 13)); 
     quit->setMinimumSize(120, 35); 
     quit->setFocusPolicy(Qt::NoFocus); 
     connect(quit, SIGNAL(clicked()), qApp, SLOT(quit())); 

     QVBoxLayout *layout = new QVBoxLayout(this); 
     
     layout->setMargin(12); 
     layout->setSpacing(8); 
     layout->addSpacing(8); 
     layout->addWidget(option1); 
     layout->addWidget(option2); 
     layout->addWidget(option3); 
     layout->addWidget(option4); 
     layout->addWidget(option5); 
     layout->addSpacing(25); 
     layout->addWidget(quit); 
     
     groupBox->setLayout(layout); 

     return groupBox; 
     } 

void teasMenu::chooseOption1()
     {
     QTextStream out(stdout); 
     out << "Option 1 selected\n" ; 
     // if ( timeScan->isVisible() )
     //   timeScan->close(); 
     // if ( mokeLoop->isVisible() )
     //   mokeLoop->close(); 
     // procMonitor->show(); 
     option1->setChecked(false); 
     } 

void teasMenu::chooseOption2()
     {
     QTextStream out(stdout);
     out << "Option 2 selected\n" ; 
     // timeScan = new configScan; 
     // if ( mokeLoop->isVisible() )
     //      mokeLoop->close(); 
     // if ( procMonitor->isVisible() )
     //      procMonitor->close(); 
     // timeScan->show(); 
     }

void teasMenu::chooseOption3()
     {
     QTextStream out(stdout);
     out << "Option 3 selected\n" ; 
     // mokeLoop = new configMoke; 
     // if ( timeScan->isVisible() )
     //      timeScan->close(); 
     // if ( procMonitor->isVisible() )
     //      procMonitor->close(); 
     // mokeLoop->show(); 
     }

void teasMenu::chooseOption4()
     {
     QTextStream out(stdout);
     out << "Option 4 selected\n" ; 
     // profScan = new configProfile;      
     // if ( timeScan->isVisible() )
     //      timeScan->close(); 
     // if ( mokeLoop->isVisible() )
     //      mokeLoop->close(); 
     // if ( procMonitor->isVisible() )
     //      procMonitor->close(); 
     // profScan->show(); 
     // connect(profScan, SIGNAL(profPlotClosed(bool)), this, SLOT(unCheckButtons())); 
     }
 
void teasMenu::chooseOption5()
     {
     QTextStream out(stdout);
     out << "Option 5 selected\n" ; 
     // tempScan = new configTemp; 
     // if ( timeScan->isVisible() )
     //      timeScan->close(); 
     // if ( mokeLoop->isVisible() )
     //      mokeLoop->close(); 
     // tempScan->show(); 
     // connect(tempScan, SIGNAL(profPlotClosed(bool)), this, SLOT(unCheckButtons())); 
     }

void teasMenu::unCheckButtons()
     { 
     if ( option4->isChecked() ) 
          { 
          option4->setChecked(false); 
          // option3->setChecked(true); 
          } 
     repaint(); 
     } 

int main(int argc, char *argv[])
     {
     QApplication app(argc, argv);
     teasMenu tm;
	tm.setGeometry(50, 50, 300, 380); 
     tm.show(); 
     return app.exec();
     }

