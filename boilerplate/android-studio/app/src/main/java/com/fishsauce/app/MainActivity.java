package com.fishsauce.app;

import android.os.Bundle;
import android.widget.TextView;
import androidx.appcompat.app.AppCompatActivity;

public class MainActivity extends AppCompatActivity {
    private final SayHelloActivity sayHello = new SayHelloActivity();

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.home);
        
        sayHello.start(findViewById(R.id.txtHello), findViewById(R.id.txtHelp));
    }

    @Override
    protected void onDestroy() {
        super.onDestroy();
        sayHello.cancel();
    }
}