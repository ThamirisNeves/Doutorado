% EEGLAB history file generated on the 05-Nov-2024
% ------------------------------------------------
[ALLEEG EEG CURRENTSET ALLCOM] = eeglab;
eeglab('redraw');
EEG = pop_biosig('C:\Users\Marcel Nascimento\Documents\Aquisição de Dados_Andreia_Gisele_HSM\TestdataANDREIA_GISELE_20241101_marcha.bdf');
[ALLEEG EEG CURRENTSET] = pop_newset(ALLEEG, EEG, 0,'gui','off'); 
pop_eegplot( EEG, 1, 1, 1);
EEG = pop_epoch( EEG, {  'condition 1'  }, [-1  2], 'newname', 'BDF file epochs', 'epochinfo', 'yes');
[ALLEEG EEG CURRENTSET] = pop_newset(ALLEEG, EEG, 1,'gui','off'); 
EEG = pop_eegfiltnew(EEG, 'locutoff',0.5,'plotfreqz',1);
[ALLEEG EEG CURRENTSET] = pop_newset(ALLEEG, EEG, 2,'gui','off'); 
eeglab redraw;
