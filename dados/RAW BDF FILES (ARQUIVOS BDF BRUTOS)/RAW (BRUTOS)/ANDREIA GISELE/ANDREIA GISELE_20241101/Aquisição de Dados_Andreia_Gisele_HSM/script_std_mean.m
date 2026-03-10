 A=randn(2,3000);
 A(1,:)=2*A(1,:)+5;
 A(2,:)=.5*A(2,:)-3;
 
 plot(A(1,:))
 hold on
 plot(A(2,:))
 
 [M, N]=size(EEG.data);
 
 EEG.data=(EEG.data-mean(EEG.data,2)*ones(1,N))./(std(EEG.data,0,2)*ones(1,N));
 
 mean(B,2)
 std(B,0,2)